"""规划节点 - 分解研究主题，制定搜索策略"""
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from app.core.state import ResearchState
from app.services.llm import get_llm
from app.config import settings


PLANNING_SYSTEM_PROMPT = """你是一个专业的研究规划专家。你的任务是分析用户的研究主题，制定详细的研究计划。

你需要：
1. 深入理解研究主题的各个维度
2. 将主题分解为可执行的子问题
3. 设计多样化的搜索查询策略
4. 规划合理的研究深度和广度

研究深度说明：
- quick: 1轮搜索，5-10个来源，快速概览
- standard: 2轮搜索，15-20个来源，全面分析
- deep: 3轮搜索，30+个来源，深度研究

你必须以JSON格式返回研究计划，格式如下：
{
    "topic": "原始主题",
    "sub_questions": ["子问题1", "子问题2", "子问题3", ...],
    "search_queries": ["查询1", "查询2", "查询3", ...],
    "search_strategy": {
        "rounds": 搜索轮数,
        "sources_per_round": 每轮来源数,
        "focus_areas": ["重点关注领域1", "重点领域2"]
    },
    "expected_outputs": ["预期产出1", "预期产出2"],
    "estimated_time_minutes": 预计时间（分钟）
}"""

PLANNING_USER_TEMPLATE = """请为以下研究主题制定详细的研究计划：

研究主题: {topic}
研究深度: {depth}

要求：
1. 子问题要覆盖主题的各个关键维度
2. 搜索查询要多样化，每个子问题至少2个查询
3. 查询应该具体且有针对性
4. 搜索策略要与深度级别匹配

请只返回JSON格式的研究计划，不要包含其他说明文字。"""


async def planning_node(state: ResearchState) -> ResearchState:
    """
    规划节点：分解研究主题，制定搜索策略
    
    Args:
        state: 当前状态
        
    Returns:
        更新后的状态
    """
    try:
        # 获取LLM
        llm = get_llm()
        
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
            "depth": state["depth"]
        })
        
        # 更新成本追踪
        cost_tracker = state.get("cost_tracker", {})
        cost_tracker["llm_calls"] = cost_tracker.get("llm_calls", 0) + 1
        
        # 更新状态
        state["plan"] = result
        state["search_queries"] = result.get("search_queries", [])
        state["stage"] = "searching"
        state["cost_tracker"] = cost_tracker
        
    except Exception as e:
        state["error_messages"] = state.get("error_messages", []) + [f"Planning error: {str(e)}"]
        state["stage"] = "failed"
    
    return state
