"""Serper.dev 搜索服务 - 免费且稳定

Serper.dev 特点：
- 免费额度：每月 2500 次调用
- 无需信用卡
- Google 搜索结果
- 速度快，稳定性高
"""
import asyncio
from typing import List, Dict, Any, Union
import httpx
from app.config import settings


class SerperSearchError(Exception):
    """Serper 搜索错误"""
    pass


class SerperSearchService:
    """Serper.dev 搜索服务"""

    def __init__(self, api_key: Union[str, None] = None):
        """
        初始化 Serper 搜索服务

        Args:
            api_key: Serper API Key（如果为 None，从环境变量读取）
        """
        self.api_key = api_key or settings.SERPER_API_KEY
        
        if not self.api_key:
            print("[Serper] 警告: 未配置 SERPER_API_KEY")
        else:
            print(f"[Serper] 初始化搜索服务 (API Key: {self.api_key[:10]}...)")
        
        self.client = httpx.AsyncClient(
            timeout=30.0,
            headers={
                "X-API-KEY": self.api_key or "",
                "Content-Type": "application/json"
            }
        )

    async def search(
        self,
        query: str,
        max_results: int = 10,
        timeout: int = 30
    ) -> List[Dict[str, Any]]:
        """
        执行 Serper 搜索

        Args:
            query: 搜索查询
            max_results: 最大结果数
            timeout: 超时时间（秒）

        Returns:
            搜索结果列表
        """
        if not self.api_key:
            raise SerperSearchError("SERPER_API_KEY 未配置")

        try:
            print(f"[Serper] 搜索: {query}")

            # Serper API 端点
            url = "https://google.serper.dev/search"
            
            # 请求参数 - 添加 gl 和 hl 参数，以及请求更多内容
            payload = {
                "q": query,
                "num": max_results,
                "gl": "cn",  # 地区：中国
                "hl": "zh-cn",  # 语言：简体中文
            }

            # 执行搜索
            response = await self.client.post(
                url,
                json=payload,
                timeout=timeout
            )

            if response.status_code != 200:
                raise SerperSearchError(f"HTTP {response.status_code}: {response.text}")

            # 解析响应
            data = response.json()
            results = self._parse_results(data, query, max_results)

            print(f"[Serper] 找到 {len(results)} 个结果")
            return results

        except asyncio.TimeoutError:
            raise SerperSearchError(f"搜索超时 ({timeout}秒)")
        except Exception as e:
            print(f"[Serper] 搜索失败: {str(e)}")
            raise SerperSearchError(f"搜索失败: {str(e)}")

    def _parse_results(self, data: Dict, query: str, max_results: int) -> List[Dict[str, Any]]:
        """
        解析 Serper 搜索结果

        Args:
            data: Serper API 响应
            query: 搜索查询
            max_results: 最大结果数

        Returns:
            搜索结果列表
        """
        results = []
        
        # Serper 返回的 organic 结果
        organic_results = data.get("organic", [])
        
        for i, item in enumerate(organic_results[:max_results]):
            result = {
                "url": item.get("link", ""),
                "title": item.get("title", ""),
                "content": item.get("snippet", ""),
                "snippet": item.get("snippet", "")[:300],
                "score": 1.0 - i * 0.1,  # 简单的评分
                "raw_content": item.get("snippet", ""),
            }
            results.append(result)
        
        return results

    async def close(self):
        """关闭 HTTP 客户端"""
        await self.client.aclose()
