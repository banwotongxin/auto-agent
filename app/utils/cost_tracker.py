"""成本追踪工具"""
from typing import Dict, Any
from app.services.llm import LLMService
from app.config import settings


class CostTrackerUtil:
    """成本追踪工具类"""
    
    @staticmethod
    def estimate_llm_cost(
        provider: str,
        model: str,
        input_tokens: int,
        output_tokens: int
    ) -> float:
        """
        估算LLM调用成本
        
        Args:
            provider: 提供商
            model: 模型名称
            input_tokens: 输入token数
            output_tokens: 输出token数
            
        Returns:
            估算成本（美元）
        """
        input_cost_per_1k, output_cost_per_1k = LLMService.get_cost_per_token(
            provider, model
        )
        
        input_cost = (input_tokens / 1000) * input_cost_per_1k
        output_cost = (output_tokens / 1000) * output_cost_per_1k
        
        return input_cost + output_cost
    
    @staticmethod
    def estimate_search_cost(search_calls: int) -> float:
        """
        估算搜索成本
        
        Tavily: 免费层1000次/月，付费约$0.025/次
        
        Args:
            search_calls: 搜索调用次数
            
        Returns:
            估算成本（美元）
        """
        # Tavily付费估算
        return search_calls * 0.025
    
    @classmethod
    def calculate_total_cost(cls, cost_tracker: Dict[str, Any]) -> float:
        """计算总成本"""
        llm_cost = cost_tracker.get("estimated_cost", 0)
        search_cost = cls.estimate_search_cost(
            cost_tracker.get("search_calls", 0)
        )
        
        return llm_cost + search_cost
    
    @classmethod
    def check_budget(cls, cost_tracker: Dict[str, Any]) -> bool:
        """检查是否超出预算"""
        if not settings.ENABLE_COST_TRACKING:
            return True
        
        total_cost = cls.calculate_total_cost(cost_tracker)
        return total_cost <= settings.MAX_COST_PER_RESEARCH
