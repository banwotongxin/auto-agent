"""网页解析服务"""
import asyncio
from typing import Optional
import aiohttp
from bs4 import BeautifulSoup
from app.config import settings


class WebParser:
    """网页内容解析器"""
    
    def __init__(self):
        self.timeout = aiohttp.ClientTimeout(total=settings.REQUEST_TIMEOUT)
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """获取或创建HTTP会话"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(timeout=self.timeout)
        return self.session
    
    async def parse(self, url: str) -> str:
        """
        解析网页内容
        
        Args:
            url: 网页URL
            
        Returns:
            提取的文本内容
        """
        try:
            session = await self._get_session()
            
            headers = {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                )
            }
            
            async with session.get(url, headers=headers, ssl=False) as response:
                if response.status != 200:
                    return f""
                
                html = await response.text()
                return self._extract_text(html)
                
        except Exception as e:
            return f""
    
    def _extract_text(self, html: str) -> str:
        """从HTML中提取文本"""
        soup = BeautifulSoup(html, 'html.parser')
        
        # 移除脚本和样式元素
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()
        
        # 获取文本
        text = soup.get_text()
        
        # 清理文本
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        # 限制长度
        return text[:settings.MAX_CONTENT_LENGTH]
    
    async def close(self):
        """关闭会话"""
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
