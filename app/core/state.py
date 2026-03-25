"""LangGraph状态定义"""
from typing import TypedDict, List, Dict, Any, Optional
from datetime import datetime
from app.models.schemas import (
    ResearchPlan,
    SearchResult,
    Source,
    Finding,
    CostTracker
)


# LangGraph State定义
class ResearchState(TypedDict, total=False):
    """研究工作流状态
    
    这是LangGraph工作流的状态类型定义，所有节点函数
    接收和返回此类型的状态对象。
    """
    # 会话信息
    session_id: str
    topic: str
    depth: str
    stage: str
    created_at: str
    
    # 规划阶段
    plan: Optional[Dict[str, Any]]
    search_queries: List[str]
    
    # 收集阶段
    search_results: List[Dict[str, Any]]
    sources: List[Dict[str, Any]]
    
    # 分析阶段
    findings: List[Dict[str, Any]]
    analysis_summary: Optional[str]
    
    # 生成阶段
    report_outline: Optional[Dict[str, Any]]
    report_sections: List[Dict[str, Any]]
    final_report: Optional[str]
    
    # 控制和元信息
    iteration_count: int
    cost_tracker: Dict[str, Any]
    error_messages: List[str]
    should_continue: bool


def create_initial_state(
    session_id: str,
    topic: str,
    depth: str = "standard"
) -> ResearchState:
    """创建初始状态"""
    return {
        "session_id": session_id,
        "topic": topic,
        "depth": depth,
        "stage": "initialized",
        "created_at": datetime.now().isoformat(),
        "plan": None,
        "search_queries": [],
        "search_results": [],
        "sources": [],
        "findings": [],
        "analysis_summary": None,
        "report_outline": None,
        "report_sections": [],
        "final_report": None,
        "iteration_count": 0,
        "cost_tracker": {
            "llm_calls": 0,
            "search_calls": 0,
            "tokens_input": 0,
            "tokens_output": 0,
            "estimated_cost": 0.0
        },
        "error_messages": [],
        "should_continue": True
    }
