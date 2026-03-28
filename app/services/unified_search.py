"""统一搜索服务 - 使用 Serper.dev

Serper.dev 特点：
- 免费额度：每月 2500 次调用
- 无需信用卡
- 速度快，稳定性高
- Google 搜索结果
"""
import asyncio
from typing import List, Dict, Any
from app.config import settings
from app.services.serper_search import SerperSearchService


class UnifiedSearchError(Exception):
    """统一搜索错误"""
    pass


class UnifiedSearchService:
    """统一搜索服务 - 使用 Serper.dev"""

    def __init__(self):
        """初始化 Serper 搜索服务"""
        if not settings.SERPER_API_KEY:
            raise UnifiedSearchError("SERPER_API_KEY 未配置，请在 .env 中设置")
        
        print(f"[SEARCH] 初始化 Serper 搜索服务 (API Key: {settings.SERPER_API_KEY[:10]}...)")
        self.service = SerperSearchService(settings.SERPER_API_KEY)

    async def search(
        self,
        query: str,
        max_results: int = 10,
        timeout: int = 30,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        执行搜索

        Args:
            query: 搜索查询
            max_results: 最大结果数
            timeout: 超时时间（秒）
            **kwargs: 其他参数（兼容性保留）

        Returns:
            搜索结果列表
            
        Raises:
            UnifiedSearchError: 搜索失败时抛出异常
        """
        try:
            results = await self.service.search(
                query=query,
                max_results=max_results,
                timeout=timeout
            )

            # 统一结果格式
            return self._normalize_results(results)

        except Exception as e:
            error_msg = f"搜索失败: {str(e)}"
            print(f"[SEARCH] {error_msg}")
            raise UnifiedSearchError(error_msg)

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
        return await self.service.batch_search(queries, max_results_per_query)

    def _normalize_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        统一结果格式

        Args:
            results: 原始搜索结果

        Returns:
            标准化后的结果
        """
        normalized = []
        for result in results:
            normalized_result = {
                "url": result.get("url", ""),
                "title": result.get("title", ""),
                "content": result.get("content", ""),
                "snippet": result.get("snippet", "")[:300],
                "score": result.get("score", 0),
                "raw_content": result.get("raw_content", result.get("content", "")),
            }
            normalized.append(normalized_result)
        return normalized

    async def close(self):
        """关闭搜索服务"""
        if hasattr(self.service, 'close'):
            await self.service.close()

