"""数据模型定义

自动深度研究智能体的数据模型，包含：
1. 研究相关的核心数据模型
2. API请求/响应模型
3. 内部状态模型
"""
from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class SearchResult(BaseModel):
    """搜索结果"""
    url: str = Field(description="来源URL")
    title: str = Field(description="来源标题")
    content: str = Field(description="提取的正文内容")
    snippet: str = Field(default="", description="搜索结果摘要")
    score: float = Field(default=0.0, description="搜索相关性分数")
    source_type: str = Field(default="web", description="来源类型: web/academic/news/wiki/blog")
    credibility_score: float = Field(default=0.5, description="可信度评分 0-1")
    extracted_at: datetime = Field(default_factory=datetime.now, description="提取时间")


class Source(BaseModel):
    """筛选后的资料源"""
    url: str = Field(description="来源URL")
    title: str = Field(description="来源标题")
    content: str = Field(description="完整正文内容")
    relevance_score: float = Field(description="相关性评分 0-1")
    credibility_score: float = Field(description="可信度评分 0-1")
    key_points: List[str] = Field(default_factory=list, description="提取的关键点")
    source_type: str = Field(default="web", description="来源类型")
    combined_score: Optional[float] = Field(default=None, description="综合评分")
    word_count: Optional[int] = Field(default=None, description="字数统计")


class ResearchPlan(BaseModel):
    """研究计划"""
    topic: str = Field(description="研究主题")
    topic_analysis: Optional[str] = Field(default=None, description="主题分析")
    sub_questions: List[str] = Field(default_factory=list, description="子问题列表")
    search_queries: List[str] = Field(default_factory=list, description="搜索查询列表")
    search_strategy: Dict[str, Any] = Field(default_factory=dict, description="搜索策略配置")
    expected_outputs: List[str] = Field(default_factory=list, description="预期产出")
    estimated_time_minutes: int = Field(default=20, description="预估时间（分钟）")
    risk_assessment: Optional[str] = Field(default=None, description="风险评估")


class Finding(BaseModel):
    """研究发现"""
    topic: str = Field(description="发现主题")
    content: str = Field(description="详细内容")
    supporting_sources: List[str] = Field(default_factory=list, description="支持来源URL列表")
    confidence: float = Field(description="可信度评分 0-1")
    evidence_strength: Optional[str] = Field(default=None, description="证据强度: strong/moderate/weak")


class CostTracker(BaseModel):
    """成本追踪"""
    llm_calls: int = Field(default=0, description="LLM调用次数")
    search_calls: int = Field(default=0, description="搜索API调用次数")
    tokens_input: int = Field(default=0, description="输入Token数")
    tokens_output: int = Field(default=0, description="输出Token数")
    estimated_cost: float = Field(default=0.0, description="估算成本（美元）")


class SourceStats(BaseModel):
    """来源统计"""
    total_sources: int = Field(description="总来源数")
    source_types: Dict[str, int] = Field(default_factory=dict, description="各类型来源数量")
    avg_credibility: float = Field(description="平均可信度")
    avg_relevance: float = Field(description="平均相关性")
    high_quality_count: int = Field(description="高质量来源数")


class QualityReport(BaseModel):
    """质量报告"""
    passed: bool = Field(description="是否通过质量检查")
    overall_score: float = Field(description="综合质量分数 0-1")
    checks: Dict[str, Any] = Field(default_factory=dict, description="各项检查结果")
    recommendation: str = Field(description="建议: completed/needs_more_search/needs_reanalysis")
    improvement_suggestions: List[str] = Field(default_factory=list, description="改进建议")


class ResearchRequest(BaseModel):
    """研究请求"""
    topic: str = Field(..., min_length=5, description="研究主题")
    depth: str = Field(
        default="standard", 
        description="研究深度 (quick/standard/deep)"
    )
    custom_instructions: Optional[str] = Field(
        default=None, 
        description="自定义指令"
    )


class ResearchResponse(BaseModel):
    """研究响应"""
    session_id: str = Field(description="会话ID")
    status: str = Field(description="状态: initialized/running/completed/failed")
    message: str = Field(description="响应消息")


class ResearchStatus(BaseModel):
    """研究状态"""
    session_id: str = Field(description="会话ID")
    status: str = Field(description="状态")
    progress: int = Field(default=0, description="进度百分比 0-100")
    stage: str = Field(description="当前阶段")
    current_action: str = Field(description="当前操作描述")
    report: Optional[str] = Field(default=None, description="生成的研究报告")
    sources: Optional[List[Dict[str, Any]]] = Field(default=None, description="来源列表")
    findings: Optional[List[Dict[str, Any]]] = Field(default=None, description="研究发现列表")
    cost_estimate: Optional[float] = Field(default=None, description="估算成本")
    quality_score: Optional[float] = Field(default=None, description="质量评分")
    error_message: Optional[str] = Field(default=None, description="错误信息")
    created_at: Optional[datetime] = Field(default=None, description="创建时间")
    updated_at: Optional[datetime] = Field(default=None, description="更新时间")
