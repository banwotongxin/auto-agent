"""DuckDuckGo 搜索服务 - 完全免费，无需 API Key

DuckDuckGo 是一个注重隐私的搜索引擎，提供免费的搜索 API
"""
import asyncio
import re
from typing import List, Dict, Any, Union
import httpx
from app.config import settings


class DuckDuckGoSearchError(Exception):
    """DuckDuckGo 搜索错误"""
    pass


class DuckDuckGoSearchService:
    """DuckDuckGo 搜索服务 - 完全免费"""

    def __init__(self, api_key: Union[str, None] = None):
        """
        初始化 DuckDuckGo 搜索服务

        Args:
            api_key: 不需要 API Key，保留参数为了接口一致性
        """
        print("[DuckDuckGo] 初始化搜索服务（完全免费，无需 API Key）")
        self.client = httpx.AsyncClient(
            timeout=30.0,
            follow_redirects=True,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "gzip, deflate, br",
                "DNT": "1",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
            }
        )

    async def search(
        self,
        query: str,
        max_results: int = 10,
        timeout: int = 30
    ) -> List[Dict[str, Any]]:
        """
        执行 DuckDuckGo 搜索

        Args:
            query: 搜索查询
            max_results: 最大结果数
            timeout: 超时时间（秒）

        Returns:
            搜索结果列表
        """
        try:
            print(f"[DuckDuckGo] 搜索: {query}")

            # 使用 DuckDuckGo HTML 版本进行搜索
            search_url = "https://html.duckduckgo.com/html/"
            params = {
                "q": query,
                "kl": "us-en",  # 改用英语，避免地区限制
            }

            # 执行搜索
            response = await self.client.get(
                search_url,
                params=params,
                timeout=timeout
            )

            if response.status_code == 202:
                # 202 通常是反爬虫，等待后重试
                print(f"[DuckDuckGo] 收到 202 响应，等待 2 秒后重试...")
                await asyncio.sleep(2)
                response = await self.client.get(
                    search_url,
                    params=params,
                    timeout=timeout
                )

            if response.status_code != 200:
                print(f"[DuckDuckGo] HTTP {response.status_code}，搜索失败")
                return []

            # 解析 HTML 响应
            html = response.text
            results = self._parse_results(html, query, max_results)

            print(f"[DuckDuckGo] 找到 {len(results)} 个结果")
            return results

        except asyncio.TimeoutError:
            raise DuckDuckGoSearchError(f"搜索超时 ({timeout}秒)")
        except Exception as e:
            print(f"[DuckDuckGo] 搜索失败: {str(e)}")
            raise DuckDuckGoSearchError(f"搜索失败: {str(e)}")

    def _parse_results(self, html: str, query: str, max_results: int) -> List[Dict[str, Any]]:
        """
        解析 DuckDuckGo 搜索结果

        Args:
            html: HTML 内容
            query: 搜索查询
            max_results: 最大结果数

        Returns:
            搜索结果列表
        """
        results = []

        # DuckDuckGo HTML 结果格式：
        # <a rel="nofollow" class="result__a" href="...">标题</a>
        # <a class="result__url" href="...">URL</a>
        # <a class="result__snippet">描述</a>

        # 提取标题和链接
        title_pattern = r'<a[^>]*class="result__a"[^>]*href="([^"]*)"[^>]*>(.*?)</a>'
        titles = re.findall(title_pattern, html, re.DOTALL)

        # 提取描述
        snippet_pattern = r'<a[^>]*class="result__snippet"[^>]*>(.*?)</a>'
        snippets = re.findall(snippet_pattern, html, re.DOTALL)

        # 合并结果
        for i in range(min(len(titles), max_results)):
            url, title = titles[i]
            snippet = snippets[i] if i < len(snippets) else ""

            # 清理 HTML 标签
            title = re.sub(r'<[^>]+>', '', title).strip()
            snippet = re.sub(r'<[^>]+>', '', snippet).strip()

            # 处理 URL（DuckDuckGo 使用重定向）
            if url.startswith("//"):
                url = "https:" + url
            elif url.startswith("/"):
                # 提取实际 URL
                url_match = re.search(r'uddg=([^&]+)', url)
                if url_match:
                    url = url_match.group(1)
                else:
                    url = "https://duckduckgo.com" + url

            # 计算相关性分数
            score = self._calculate_score(title, snippet, query)

            result = {
                "url": url,
                "title": title,
                "content": snippet if snippet else title,
                "snippet": snippet[:300] if snippet else title[:300],
                "score": score,
                "raw_content": snippet if snippet else title,
            }

            results.append(result)

        return results

    def _calculate_score(self, title: str, snippet: str, query: str) -> float:
        """
        计算相关性分数

        Args:
            title: 标题
            snippet: 描述
            query: 查询

        Returns:
            分数 (0-1)
        """
        # 查询词在标题中的出现
        query_lower = query.lower()
        title_lower = title.lower()
        snippet_lower = snippet.lower()

        score = 0.0

        # 标题匹配
        if query_lower in title_lower:
            score += 0.5

        # 描述匹配
        if query_lower in snippet_lower:
            score += 0.3

        # 内容长度（适中的长度更好）
        total_len = len(title) + len(snippet)
        if 100 <= total_len <= 300:
            score += 0.2

        return min(score, 1.0)

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
        results = {}

        for query in queries:
            try:
                query_results = await self.search(query, max_results=max_results_per_query)
                results[query] = query_results
                # 避免请求过快
                await asyncio.sleep(1)
            except Exception as e:
                print(f"[DuckDuckGo] 查询 '{query}' 失败: {str(e)}")
                results[query] = []

        return results

    async def close(self):
        """关闭 HTTP 客户端"""
        await self.client.aclose()
