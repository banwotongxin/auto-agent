"""LLM服务封装"""
from typing import Optional, Any
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from langchain_core.language_models import BaseChatModel
from app.config import settings


class LLMService:
    """LLM服务管理器"""
    
    _instances: dict = {}
    
    @classmethod
    def get_llm(
        cls,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> BaseChatModel:
        """
        获取LLM实例
        
        Args:
            provider: 提供商 (anthropic/openai)
            model: 模型名称
            temperature: 温度参数
            max_tokens: 最大Token数
            
        Returns:
            LLM实例
        """
        provider = provider or settings.DEFAULT_LLM_PROVIDER
        model = model or settings.DEFAULT_MODEL
        temperature = temperature or settings.TEMPERATURE
        max_tokens = max_tokens or settings.MAX_TOKENS
        
        # 缓存键
        cache_key = f"{provider}:{model}:{temperature}:{max_tokens}"
        
        if cache_key not in cls._instances:
            if provider == "anthropic":
                if not settings.ANTHROPIC_API_KEY:
                    raise ValueError("ANTHROPIC_API_KEY not configured")
                    
                cls._instances[cache_key] = ChatAnthropic(
                    model=model,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    anthropic_api_key=settings.ANTHROPIC_API_KEY,
                )
                
            elif provider == "openai":
                if not settings.OPENAI_API_KEY:
                    raise ValueError("OPENAI_API_KEY not configured")

                # 检查是否配置了自定义API Base
                api_base = getattr(settings, 'OPENAI_API_BASE', None)

                cls._instances[cache_key] = ChatOpenAI(
                    model=model,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    api_key=settings.OPENAI_API_KEY,
                    base_url=api_base if api_base else None,
                )
            else:
                raise ValueError(f"Unsupported LLM provider: {provider}")
        
        return cls._instances[cache_key]
    
    @classmethod
    def get_cost_per_token(cls, provider: str, model: str) -> tuple:
        """
        获取Token成本 (输入, 输出)
        
        Returns:
            (input_cost_per_1k, output_cost_per_1k) 单位：美元
        """
        costs = {
            "anthropic": {
                "claude-3-opus-20240229": (0.015, 0.075),
                "claude-3-sonnet-20240229": (0.003, 0.015),
                "claude-3-haiku-20240307": (0.00025, 0.00125),
            },
            "openai": {
                "gpt-4o": (0.005, 0.015),
                "gpt-4o-mini": (0.00015, 0.0006),
                "gpt-4-turbo": (0.01, 0.03),
            }
        }
        
        provider_costs = costs.get(provider, {})
        return provider_costs.get(model, (0.003, 0.015))  # 默认成本


# 便捷函数
def get_llm(**kwargs) -> BaseChatModel:
    """获取LLM实例的便捷函数"""
    return LLMService.get_llm(**kwargs)
