"""搜索服务"""
import asyncio
from typing import List, Dict, Any, Optional
from tavily import TavilyClient
from app.config import settings


class SearchService:
    """搜索服务"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.TAVILY_API_KEY
        if not self.api_key:
            raise ValueError("TAVILY_API_KEY not configured")
        
        self.client = TavilyClient(api_key=self.api_key)
    
    async def search(
        self,
        query: str,
        max_results: int = 10,
        search_depth: str = "advanced",
        include_answer: bool = False,
        include_raw_content: bool = True
    ) -> List[Dict[str, Any]]:
        """
        执行 Tavily 搜索
        
        Args:
            query: 搜索查询
            max_results: 最大结果数
            search_depth: basic 或 advanced
            include_answer: 是否包含AI生成的答案
            include_raw_content: 是否包含原始网页内容
            
        Returns:
            搜索结果列表
        """
        try:
            # Tavily客户端是同步的，在线程池中运行
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.client.search(
                    query=query,
                    max_results=max_results,
                    search_depth=search_depth,
                    include_answer=include_answer,
                    include_raw_content=include_raw_content
                )
            )
            
            results = []
            for item in response.get("results", []):
                results.append({
                    "url": item.get("url"),
                    "title": item.get("title"),
                    "content": item.get("content", ""),
                    "snippet": item.get("content", "")[:300],
                    "score": item.get("score", 0),
                    "raw_content": item.get("raw_content", ""),
                    "extracted_at": asyncio.get_event_loop().time()
                })
            
            return results
            
        except Exception as e:
            raise SearchError(f"Search failed for query '{query}': {str(e)}")
    
    async def batch_search(
        self,
        queries: List[str],
        max_results_per_query: int = 5
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        批量执行搜索
        
        Args:
            queries: 查询列表
            max_results_per_query: 每个查询的最大结果数
            
        Returns:
            按查询分组的结果
        """
        tasks = [
            self.search(q, max_results=max_results_per_query)
            for q in queries
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return {
            query: result if not isinstance(result, Exception) else []
            for query, result in zip(queries, results)
        }


class SearchError(Exception):
    """搜索错误"""
    pass
