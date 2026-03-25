"""LangGraph工作流图构建"""
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from app.core.state import ResearchState
from app.core.nodes import (
    planning_node,
    searching_node,
    analyzing_node,
    generating_node,
    quality_check_node,
    route_decision
)


def create_research_graph() -> StateGraph:
    """
    创建研究工作流图
    
    工作流：
    planner -> searcher -> analyzer -> generator -> quality_check
                                        ↑           ↓
                                        └─(needs_reanalysis)─↓
                                (needs_more_search)──────────┘
    
    Returns:
        编译后的状态图
    """
    
    # 创建工作流
    workflow = StateGraph(ResearchState)
    
    # 添加节点
    workflow.add_node("planner", planning_node)
    workflow.add_node("searcher", searching_node)
    workflow.add_node("analyzer", analyzing_node)
    workflow.add_node("generator", generating_node)
    workflow.add_node("quality_check", quality_check_node)
    
    # 设置入口点
    workflow.set_entry_point("planner")
    
    # 添加普通边
    workflow.add_edge("planner", "searcher")
    workflow.add_edge("searcher", "analyzer")
    workflow.add_edge("analyzer", "generator")
    workflow.add_edge("generator", "quality_check")
    
    # 质量检查后的条件路由
    workflow.add_conditional_edges(
        "quality_check",
        route_decision,
        {
            "needs_more_search": "searcher",
            "needs_reanalysis": "analyzer",
            "completed": END,
            "failed": END
        }
    )
    
    # 编译图，使用内存检查点
    memory = MemorySaver()
    return workflow.compile(checkpointer=memory)


# 全局图实例
_research_graph = None


def get_research_graph() -> StateGraph:
    """获取研究工作流图单例"""
    global _research_graph
    if _research_graph is None:
        _research_graph = create_research_graph()
    return _research_graph
