"""全局配置管理"""
from functools import lru_cache
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """应用配置类"""
    
    # 应用配置
    APP_NAME: str = Field(default="AutoResearch Agent", description="应用名称")
    APP_VERSION: str = Field(default="1.0.0", description="应用版本")
    DEBUG: bool = Field(default=False, description="调试模式")
    
    # API配置
    API_HOST: str = Field(default="0.0.0.0", description="API监听地址")
    API_PORT: int = Field(default=8000, description="API端口")
    API_WORKERS: int = Field(default=1, description="工作进程数")
    
    # LLM配置
    DEFAULT_LLM_PROVIDER: str = Field(
        default="anthropic", 
        description="默认LLM提供商 (anthropic/openai)"
    )
    ANTHROPIC_API_KEY: Optional[str] = Field(
        default=None, 
        description="Anthropic API密钥"
    )
    OPENAI_API_KEY: Optional[str] = Field(
        default=None, 
        description="OpenAI API密钥"
    )
    DEFAULT_MODEL: str = Field(
        default="claude-3-sonnet-20240229",
        description="默认模型"
    )
    MAX_TOKENS: int = Field(default=4000, description="最大Token数")
    TEMPERATURE: float = Field(default=0.3, description="温度参数")
    
    # 搜索配置
    TAVILY_API_KEY: Optional[str] = Field(
        default=None, 
        description="Tavily API密钥"
    )
    MAX_SEARCH_RESULTS: int = Field(default=10, description="最大搜索结果数")
    SEARCH_DEPTH: str = Field(
        default="advanced", 
        description="搜索深度 (basic/advanced)"
    )
    
    # 网页解析配置
    FIRECRAWL_API_KEY: Optional[str] = Field(
        default=None, 
        description="FireCrawl API密钥"
    )
    REQUEST_TIMEOUT: int = Field(default=30, description="请求超时(秒)")
    MAX_CONTENT_LENGTH: int = Field(
        default=100000, 
        description="最大内容长度"
    )
    
    # 向量存储配置
    CHROMA_PERSIST_DIR: str = Field(
        default="./chroma_db", 
        description="ChromaDB持久化目录"
    )
    EMBEDDING_MODEL: str = Field(
        default="sentence-transformers/all-MiniLM-L6-v2",
        description="嵌入模型"
    )
    CHUNK_SIZE: int = Field(default=1000, description="文本分块大小")
    CHUNK_OVERLAP: int = Field(default=200, description="分块重叠大小")
    
    # 研究配置
    MAX_RESEARCH_DEPTH: int = Field(default=3, description="最大研究深度")
    MAX_SEARCH_QUERIES: int = Field(default=15, description="最大搜索查询数")
    MIN_SOURCE_QUALITY: float = Field(default=0.6, description="最低来源质量")
    
    # Redis配置
    REDIS_URL: str = Field(
        default="redis://localhost:6379/0", 
        description="Redis连接URL"
    )
    
    # 成本控制
    MAX_COST_PER_RESEARCH: float = Field(
        default=5.0, 
        description="单次研究最大成本(美元)"
    )
    ENABLE_COST_TRACKING: bool = Field(
        default=True, 
        description="启用成本追踪"
    )
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    """获取配置单例"""
    return Settings()


# 全局配置实例
settings = get_settings()
