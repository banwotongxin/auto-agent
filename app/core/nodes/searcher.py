"""收集节点 - 搜索并解析信息来源

自动深度研究智能体的核心组件，负责：
1. 并行执行多个搜索查询
2. 解析网页内容提取关键信息
3. 评估来源质量和相关性
4. 去重和综合排序
"""
import asyncio
from typing import List, Dict, Any, Set, Tuple
from app.core.state import ResearchState
from app.services.search import SearchService
from app.services.parser import WebParser
from app.config import settings


class SourceEvaluator:
    """来源质量评估器"""
    
    # 高可信度域名
    HIGH_CREDIBILITY_DOMAINS = {
        # 学术机构
        ".edu", ".ac.", ".gov", ".org",
        # 学术期刊
        "nature.com", "science.org", "arxiv.org", "IEEE.org", "ACM.org",
        "researchgate.net", "scholar.google.com", "pubmed.ncbi.nlm.nih.gov",
        "sciencedirect.com", "springer.com", "wiley.com", "tandfonline.com",
        # 百科全书
        "wikipedia.org", "wikimedia.org",
        # 权威新闻
        "reuters.com", "bloomberg.com", "ap.org", "afp.com",
        "bbc.com", "nytimes.com", "theguardian.com", "wsj.com",
        # 专业机构
        "who.int", "un.org", "worldbank.org", "imf.org",
        "mit.edu", "stanford.edu", "harvard.edu", "oxford.edu"
    }
    
    # 中等可信度域名
    MEDIUM_CREDIBILITY_DOMAINS = {
        "news.", "blog.", "medium.com", "substack.com",
        "forbes.com", "techcrunch.com", "venturebeat.com",
        "hbr.org", "mckinsey.com"
    }
    
    # 低可信度域名
    LOW_CREDIBILITY_DOMAINS = {
        "blogspot.com", "wordpress.com", "weebly.com",
        "quora.com", "reddit.com", "tumblr.com"
    }
    
    @classmethod
    def assess_credibility(cls, url: str) -> Tuple[float, str]:
        """
        评估来源可信度
        
        Args:
            url: 来源URL
            
        Returns:
            (可信度分数, 来源类型)
        """
        url_lower = url.lower()
        
        # 检查高可信度域名
        for domain in cls.HIGH_CREDIBILITY_DOMAINS:
            if domain in url_lower:
                if "wikipedia" in url_lower:
                    return 0.85, "wiki"
                elif any(edu in url_lower for edu in [".edu", ".ac.", "arxiv.org", "IEEE", "ACM"]):
                    return 0.95, "academic"
                elif any(news in url_lower for news in ["reuters", "bloomberg", "ap.org", "bbc", "nytimes"]):
                    return 0.9, "news"
                return 0.9, "official"
        
        # 检查中等可信度域名
        for domain in cls.MEDIUM_CREDIBILITY_DOMAINS:
            if domain in url_lower:
                if "news" in domain or "blog" in domain:
                    return 0.6, "news/blog"
                return 0.65, "professional"
        
        # 检查低可信度域名
        for domain in cls.LOW_CREDIBILITY_DOMAINS:
            if domain in url_lower:
                return 0.3, "social"
        
        # 默认中等可信度
        return 0.5, "web"
    
    @classmethod
    def calculate_relevance(cls, content: str, query: str) -> float:
        """
        计算内容与查询的相关性分数
        
        Args:
            content: 内容文本
            query: 查询文本
            
        Returns:
            相关性分数 (0-1)
        """
        if not content or not query:
            return 0.0
        
        query_terms = set(query.lower().split())
        content_lower = content.lower()
        
        # 计算查询词在内容中的出现率
        matches = sum(1 for term in query_terms if term in content_lower)
        term_score = matches / max(len(query_terms), 1)
        
        # 内容长度权重（太长或太短都不利）
        content_len = len(content)
        if content_len < 200:
            length_score = 0.2
        elif content_len < 1000:
            length_score = 0.6
        elif content_len < 5000:
            length_score = 1.0
        elif content_len < 10000:
            length_score = 0.8
        else:
            length_score = 0.6
        
        # 标题匹配权重（如果content是标题）
        title_bonus = 0.1 if len(content) < 200 else 0
        
        # 综合分数
        return min(term_score * 0.7 + length_score * 0.3 + title_bonus, 1.0)


class ContentExtractor:
    """内容提取器"""
    
    # 关键词模式（表示高质量内容）
    QUALITY_INDICATORS = [
        "research", "study", "analysis", "data", "statistics",
        "report", "survey", " finding", "conclusion", "evidence"
    ]
    
    # 噪音内容模式
    NOISE_PATTERNS = [
        "cookie", "consent", "subscribe", "newsletter", "advertisement",
        "promo", "sponsor", "affiliate", "pop-up", "banner"
    ]
    
    @classmethod
    def extract_key_points(cls, content: str, title: str = "", max_points: int = 5) -> List[str]:
        """
        提取关键点
        
        Args:
            content: 内容文本
            title: 标题
            max_points: 最大关键点数
            
        Returns:
            关键点列表
        """
        key_points = []
        
        # 简单实现：提取包含关键词的句子
        content_lower = content.lower()
        
        for indicator in cls.QUALITY_INDICATORS:
            if indicator in content_lower:
                # 找到包含该词的句子
                sentences = content.split(". ")
                for sentence in sentences:
                    if indicator in sentence.lower() and len(sentence) > 50:
                        clean_sentence = sentence.strip()
                        if clean_sentence not in key_points:
                            key_points.append(clean_sentence)
                            break
        
        return key_points[:max_points]
    
    @classmethod
    def is_quality_content(cls, content: str, title: str = "") -> bool:
        """
        判断内容质量是否达标
        
        Args:
            content: 内容文本
            title: 标题
            
        Returns:
            是否达标
        """
        if len(content) < 300:
            return False
        
        # 检查噪音模式
        content_lower = content.lower()
        noise_count = sum(1 for pattern in cls.NOISE_PATTERNS if pattern in content_lower)
        if noise_count >= 3:
            return False
        
        # 检查质量指标
        quality_count = sum(1 for indicator in cls.QUALITY_INDICATORS if indicator in content_lower)
        
        return quality_count >= 2


class SearchNodeExecutor:
    """搜索节点执行器"""
    
    def __init__(self):
        self.search_service = SearchService()
        self.parser = WebParser()
        self.evaluator = SourceEvaluator()
        self.extractor = ContentExtractor()
    
    async def search_single_query(
        self, 
        query: str, 
        max_results: int,
        search_depth: str = "advanced"
    ) -> List[Dict[str, Any]]:
        """
        执行单个查询的搜索
        
        Args:
            query: 搜索查询
            max_results: 最大结果数
            search_depth: 搜索深度
            
        Returns:
            来源列表
        """
        sources = []
        
        try:
            # 执行搜索
            results = await self.search_service.search(
                query=query,
                max_results=max_results,
                search_depth=search_depth,
                include_raw_content=True
            )
            
            for result in results:
                try:
                    # 评估URL可信度
                    credibility, source_type = self.evaluator.assess_credibility(result["url"])
                    
                    # 解析网页内容
                    content = await self.parser.parse(result["url"])
                    
                    # 如果解析失败或内容太短，使用搜索结果中的摘要
                    if len(content) < 200:
                        content = result.get("raw_content", "") or result.get("content", "")
                    
                    # 评估相关性
                    relevance = self.evaluator.calculate_relevance(content, query)
                    
                    # 计算综合分数（相关性60% + 可信度40%）
                    combined_score = relevance * 0.6 + credibility * 0.4
                    
                    # 只保留质量达标的来源
                    min_quality = settings.MIN_SOURCE_QUALITY
                    if combined_score >= min_quality and len(content) >= 200:
                        # 提取关键点
                        key_points = self.extractor.extract_key_points(
                            content, 
                            result.get("title", "")
                        )
                        
                        source = {
                            "url": result["url"],
                            "title": result["title"],
                            "content": content[:settings.MAX_CONTENT_LENGTH],
                            "snippet": result.get("content", "")[:300],
                            "relevance_score": round(relevance, 3),
                            "credibility_score": round(credibility, 2),
                            "combined_score": round(combined_score, 3),
                            "source_type": source_type,
                            "search_query": query,
                            "key_points": key_points,
                            "word_count": len(content.split())
                        }
                        sources.append(source)
                        
                except Exception as e:
                    # 单个来源处理失败不影响整体
                    continue
            
        except Exception as e:
            # 搜索失败返回空列表
            pass
        
        return sources
    
    async def execute(self, state: ResearchState) -> ResearchState:
        """搜索节点主逻辑"""
        queries = state.get("search_queries", [])
        depth = state.get("depth", "standard")
        
        if not queries:
            state["error_messages"] = state.get("error_messages", []) + ["No search queries generated"]
            state["stage"] = "failed"
            return state
        
        # 根据深度确定每轮结果数
        depth_config = {
            "quick": {"rounds": 1, "results_per_query": 8, "max_sources": 10},
            "standard": {"rounds": 2, "results_per_query": 10, "max_sources": 20},
            "deep": {"rounds": 3, "results_per_query": 12, "max_sources": 50}
        }
        
        config = depth_config.get(depth, depth_config["standard"])
        results_per_query = config["results_per_query"]
        max_sources = config["max_sources"]
        
        # 并行执行所有搜索
        tasks = [
            self.search_single_query(q, results_per_query, settings.SEARCH_DEPTH)
            for q in queries
        ]
        
        search_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 合并和去重
        all_sources: List[Dict[str, Any]] = []
        seen_urls: Set[str] = set()
        
        for sources in search_results:
            if isinstance(sources, Exception):
                continue
            for source in sources:
                url = source["url"]
                if url not in seen_urls:
                    all_sources.append(source)
                    seen_urls.add(url)
        
        # 按综合分数排序
        all_sources.sort(
            key=lambda x: x["combined_score"],
            reverse=True
        )
        
        # 限制来源数量
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
