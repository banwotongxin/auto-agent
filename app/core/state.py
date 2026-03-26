"""LangGraph状态定义

自动深度研究智能体的核心状态定义，用于LangGraph工作流中的状态管理。
"""
from typing import TypedDict, List, Dict, Any, Optional
from datetime import datetime


class ResearchState(TypedDict, total=False):
    """
    研究工作流状态
    
    这是LangGraph工作流的状态类型定义，所有节点函数
    接收和返回此类型的状态对象。
    
    状态包含以下主要部分：
    - 会话信息：session_id, topic, depth, stage, created_at
    - 规划阶段：plan, search_queries
    - 收集阶段：search_results, sources, source_stats
    - 分析阶段：findings, analysis_summary, key_themes, information_gaps, controversial_points
    - 生成阶段：report_outline, report_sections, final_report
    - 质量控制：quality_report, quality_score, quality_suggestions
    - 控制信息：iteration_count, cost_tracker, error_messages, should_continue
    """
    
    # ==================== 会话信息 ====================
    session_id: str  # 唯一会话标识
    topic: str  # 研究主题
    depth: str  # 研究深度: quick/standard/deep
    stage: str  # 当前阶段: initialized/planning/searching/analyzing/generating/quality_check/completed/failed
    created_at: str  # 创建时间 ISO格式
    
    # ==================== 规划阶段 ====================
    plan: Optional[Dict[str, Any]]  # 完整研究计划
    search_queries: List[str]  # 提取的搜索查询列表
    
    # ==================== 收集阶段 ====================
    search_results: List[Dict[str, Any]]  # 原始搜索结果
    sources: List[Dict[str, Any]]  # 筛选后的来源列表
    source_stats: Optional[Dict[str, Any]]  # 来源统计信息
    consensus: Optional[List[str]]  # 来源间的共识
    divergence: Optional[List[str]]  # 来源间的分歧
    
    # ==================== 分析阶段 ====================
    findings: List[Dict[str, Any]]  # 关键发现列表
    analysis_summary: Optional[str]  # 分析摘要
    key_themes: List[str]  # 主要研究主题
    information_gaps: List[str]  # 信息缺口
    controversial_points: List[str]  # 争议点
    
    # ==================== 生成阶段 ====================
    report_outline: Optional[Dict[str, Any]]  # 报告大纲
    report_sections: List[Dict[str, Any]]  # 报告章节
    final_report: Optional[str]  # 最终Markdown报告
    
    # ==================== 质量控制 ====================
    quality_report: Optional[Dict[str, Any]]  # 质量检查报告
    quality_score: Optional[float]  # 质量评分 0-1
    quality_suggestions: List[str]  # 改进建议
    
    # ==================== 控制信息 ====================
    iteration_count: int  # 当前迭代次数
    cost_tracker: Dict[str, Any]  # 成本追踪
    error_messages: List[str]  # 错误消息列表
    should_continue: bool  # 是否继续循环


def create_initial_state(
    session_id: str,
    topic: str,
    depth: str = "standard"
) -> ResearchState:
    """
    创建初始研究状态
    
    Args:
        session_id: 唯一会话标识
        topic: 研究主题
        depth: 研究深度 (quick/standard/deep)
        
    Returns:
        初始化的ResearchState
    """
    return {
        # 会话信息
        "session_id": session_id,
        "topic": topic,
        "depth": depth,
        "stage": "initialized",
        "created_at": datetime.now().isoformat(),
        
        # 规划阶段
        "plan": None,
        "search_queries": [],
        
        # 收集阶段
        "search_results": [],
        "sources": [],
        "source_stats": None,
        "consensus": None,
        "divergence": None,
        
        # 分析阶段
        "findings": [],
        "analysis_summary": None,
        "key_themes": [],
        "information_gaps": [],
        "controversial_points": [],
        
        # 生成阶段
        "report_outline": None,
        "report_sections": [],
        "final_report": None,
        
        # 质量控制
        "quality_report": None,
        "quality_score": None,
        "quality_suggestions": [],
        
        # 控制信息
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
