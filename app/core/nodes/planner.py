"""规划节点 - 分解研究主题，制定搜索策略

自动深度研究智能体的核心组件之一，负责：
1. 深入理解研究主题的各个维度
2. 将主题分解为可执行的子问题
3. 设计多样化的搜索查询策略
4. 规划合理的研究深度和广度
"""
from typing import Dict, Any, List
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from app.core.state import ResearchState
from app.services.llm import get_llm
from app.config import settings


# 研究深度配置
DEPTH_CONFIG = {
    "quick": {
        "rounds": 1,
        "sources_per_round": 10,
        "min_sources": 5,
        "max_sources": 10,
        "estimated_time_minutes": 10,
        "report_length": 1500
    },
    "standard": {
        "rounds": 2,
        "sources_per_round": 15,
        "min_sources": 15,
        "max_sources": 20,
        "estimated_time_minutes": 20,
        "report_length": 3000
    },
    "deep": {
        "rounds": 3,
        "sources_per_round": 20,
        "min_sources": 30,
        "max_sources": 50,
        "estimated_time_minutes": 45,
        "report_length": 5000
    }
}

PLANNING_SYSTEM_PROMPT = """你是一个专业的研究规划专家，擅长将复杂的研究主题分解为可执行的搜索计划。

你的任务是分析用户的研究主题，制定详细的研究计划。

核心能力：
1. 深入理解研究主题的各个维度
2. 将主题分解为逻辑清晰的子问题
3. 设计多样化的搜索查询策略
4. 评估研究可行性和资源需求

研究深度级别说明：
- quick（快速模式）: 1轮搜索，5-10个来源，约10分钟
- standard（标准模式）: 2轮搜索，15-20个来源，约20分钟  
- deep（深度模式）: 3轮搜索，30+个来源，约45分钟

搜索策略设计原则：
1. 每个子问题至少对应2-3个不同的搜索查询
2. 查询要覆盖不同的角度：定义、案例、数据、观点、争议
3. 使用专业术语和多样化表述
4. 考虑不同来源类型：学术、新闻、行业报告

请以JSON格式返回研究计划，格式如下：
{
    "topic": "原始研究主题",
    "topic_analysis": "对主题的深入分析（100字以内）",
    "sub_questions": ["子问题1", "子问题2", "子问题3"],
    "search_queries": [
        {"query": "具体搜索查询", "purpose": "这个查询的目的", "角度": "覆盖的主题角度"}
    ],
    "search_strategy": {
        "rounds": 搜索轮数,
        "sources_per_round": 每轮目标来源数,
        "focus_areas": ["重点关注领域1", "重点领域2"],
        "quality_criteria": "来源质量筛选标准"
    },
    "expected_outputs": ["预期产出1", "预期产出2"],
    "estimated_time_minutes": 预计完成时间,
    "risk_assessment": "可能的风险和应对措施"
}

请只返回JSON格式的研究计划，不要包含其他说明文字。"""

PLANNING_USER_TEMPLATE = """请为以下研究主题制定详细的研究计划：

研究主题: {topic}
研究深度级别: {depth}

详细要求：
1. 子问题要覆盖主题的各个关键维度，包括定义、现状、问题、解决方案、未来趋势等
2. 搜索查询要多样化，每个子问题至少2-3个不同角度的查询
3. 查询应该具体且有针对性，避免过于宽泛
4. 搜索策略要与深度级别匹配，确保研究深度和广度
5. 评估可能遇到的风险，如信息不足、来源质量差等

请只返回JSON格式的研究计划，不要包含其他说明文字。"""


def _get_depth_config(depth: str) -> Dict[str, Any]:
    """获取指定深度的配置"""
    return DEPTH_CONFIG.get(depth, DEPTH_CONFIG["standard"])


def _extract_search_queries(plan: Dict[str, Any]) -> List[str]:
    """从计划中提取搜索查询列表"""
    search_queries = []
    
    # 尝试从search_queries字段提取
    queries_data = plan.get("search_queries", [])
    
    if isinstance(queries_data, list):
        for item in queries_data:
            if isinstance(item, str):
                search_queries.append(item)
            elif isinstance(item, dict):
                query = item.get("query", "")
                if query:
                    search_queries.append(query)
    
    return search_queries


async def planning_node(state: ResearchState) -> ResearchState:
    """
    规划节点：分解研究主题，制定搜索策略
    
    核心功能：
    1. 使用LLM深入分析研究主题
    2. 生成逻辑清晰的子问题
    3. 设计多样化的搜索查询策略
    4. 根据深度级别调整搜索计划
    
    Args:
        state: 当前状态
        
    Returns:
        更新后的状态
    """
    try:
        # 获取深度配置
        depth = state.get("depth", "standard")
        depth_config = _get_depth_config(depth)
        
        # 获取LLM
        llm = get_llm(
            max_tokens=depth_config.get("report_length", 3000)
        )
        
        # 构建提示
        prompt = ChatPromptTemplate.from_messages([
            ("system", PLANNING_SYSTEM_PROMPT),
            ("human", PLANNING_USER_TEMPLATE)
        ])
        
        # 解析器
        parser = JsonOutputParser()
        
        # 构建链
        chain = prompt | llm | parser
        
        # 执行规划
        result = await chain.ainvoke({
            "topic": state["topic"],
            "depth": depth
        })
        
        # 提取搜索查询
        search_queries = _extract_search_queries(result)
        
        # 限制查询数量
        max_queries = settings.MAX_SEARCH_QUERIES
        search_queries = search_queries[:max_queries]
        
        # 更新成本追踪
        cost_tracker = state.get("cost_tracker", {})
        cost_tracker["llm_calls"] = cost_tracker.get("llm_calls", 0) + 1
        
        # 更新状态
        state["plan"] = result
        state["search_queries"] = search_queries
        state["stage"] = "searching"
        state["cost_tracker"] = cost_tracker
        
    except Exception as e:
        state["error_messages"] = state.get("error_messages", []) + [f"Planning error: {str(e)}"]
        state["stage"] = "failed"
    
    return state
