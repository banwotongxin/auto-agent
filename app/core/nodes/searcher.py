"""收集节点 - 搜索并解析信息来源"""
import asyncio
from typing import List, Dict, Any
from app.core.state import ResearchState
from app.services.search import SearchService
from app.services.parser import WebParser
from app.config import settings


class SearchNodeExecutor:
    """搜索节点执行器"""
    
    def __init__(self):
        self.search_service = SearchService()
        self.parser = WebParser()
    
    def _calculate_relevance(self, content: str, query: str) -> float:
        """计算内容与查询的相关性分数（简单实现）"""
        query_terms = set(query.lower().split())
        content_lower = content.lower()
        
        # 计算查询词在内容中的出现率
        matches = sum(1 for term in query_terms if term in content_lower)
        score = matches / max(len(query_terms), 1)
        
        # 内容长度权重
        length_score = min(len(content) / 5000, 1.0) * 0.3
        
        return min(score * 0.7 + length_score, 1.0)
    
    def _assess_credibility(self, url: str) -> float:
        """评估来源可信度"""
        # 基于域名的可信度评估
        trusted_domains = [
            ".edu", ".gov", ".ac.", "wikipedia.org",
            "nature.com", "science.org", "arxiv.org",
            "ieee.org", "acm.org", "researchgate.net"
        ]
        
        url_lower = url.lower()
        
        # 检查可信域名
        for domain in trusted_domains:
            if domain in url_lower:
                return 0.8 + (0.1 if "wikipedia" not in url_lower else 0)
        
        # 新闻网站中等可信度
        news_domains = ["news", "reuters", "bloomberg", "cnn", "bbc"]
        if any(domain in url_lower for domain in news_domains):
            return 0.6
        
        # 博客和个人网站较低可信度
        blog_domains = ["blog", "medium", "wordpress"]
        if any(domain in url_lower for domain in blog_domains):
            return 0.4
        
        return 0.5
    
    async def search_single_query(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """执行单个查询的搜索"""
        try:
            # 执行搜索
            results = await self.search_service.search(
                query=query,
                max_results=max_results,
                search_depth=settings.SEARCH_DEPTH
            )
            
            sources = []
            for result in results:
                try:
                    # 解析网页内容
                    content = await self.parser.parse(result["url"])
                    
                    # 如果解析失败或内容太短，使用搜索结果中的摘要
                    if len(content) < 200:
                        content = result.get("raw_content", "") or result.get("content", "")
                    
                    # 计算分数
                    relevance = self._calculate_relevance(content, query)
                    credibility = self._assess_credibility(result["url"])
                    
                    # 只保留质量达标的来源
                    if relevance >= settings.MIN_SOURCE_QUALITY:
                        source = {
                            "url": result["url"],
                            "title": result["title"],
                            "content": content[:settings.MAX_CONTENT_LENGTH],
                            "relevance_score": relevance,
                            "credibility_score": credibility,
                            "search_query": query,
                            "key_points": []
                        }
                        sources.append(source)
                        
                except Exception as e:
                    continue
            
            return sources
            
        except Exception as e:
            return []
    
    async def execute(self, state: ResearchState) -> ResearchState:
        """搜索节点主逻辑"""
        queries = state.get("search_queries", [])
        
        if not queries:
            state["error_messages"] = state.get("error_messages", []) + ["No search queries generated"]
            state["stage"] = "failed"
            return state
        
        # 根据深度确定每轮结果数
        depth_config = {
            "quick": 5,
            "standard": 8,
            "deep": 10
        }
        results_per_query = depth_config.get(state["depth"], 8)
        
        # 并行执行搜索
        tasks = [
            self.search_single_query(q, results_per_query)
            for q in queries
        ]
        
        search_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 合并和去重
        all_sources = []
        seen_urls = set()
        
        for sources in search_results:
            if isinstance(sources, Exception):
                continue
            for source in sources:
                url = source["url"]
                if url not in seen_urls:
                    all_sources.append(source)
                    seen_urls.add(url)
        
        # 按综合分数排序（相关性70% + 可信度30%）
        all_sources.sort(
            key=lambda x: x["relevance_score"] * 0.7 + x["credibility_score"] * 0.3,
            reverse=True
        )
        
        # 根据深度限制来源数量
        max_sources = {
            "quick": 10,
            "standard": 20,
            "deep": 35
        }.get(state["depth"], 20)
        
        state["sources"] = all_sources[:max_sources]
        state["stage"] = "analyzing"
        
        # 更新成本追踪
        cost_tracker = state.get("cost_tracker", {})
        cost_tracker["search_calls"] = cost_tracker.get("search_calls", 0) + len(queries)
        state["cost_tracker"] = cost_tracker
        
        # 关闭解析器会话
        await self.parser.close()
        
        return state


async def searching_node(state: ResearchState) -> ResearchState:
    """搜索节点入口函数"""
    executor = SearchNodeExecutor()
    return await executor.execute(state)
