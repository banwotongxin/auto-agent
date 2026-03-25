"""数据模型定义"""
from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class SearchResult(BaseModel):
    """搜索结果"""
    url: str
    title: str
    content: str
    snippet: str = ""
    score: float = 0.0
    source_type: str = "web"
    credibility_score: float = 0.5
    extracted_at: datetime = Field(default_factory=datetime.now)


class Source(BaseModel):
    """筛选后的资料源"""
    url: str
    title: str
    content: str
    relevance_score: float
    credibility_score: float
    key_points: List[str] = Field(default_factory=list)


class ResearchPlan(BaseModel):
    """研究计划"""
    topic: str
    sub_questions: List[str]
    search_queries: List[str]
    search_strategy: Dict[str, Any]
    expected_outputs: List[str]
    estimated_time_minutes: int


class Finding(BaseModel):
    """研究发现"""
    topic: str
    content: str
    supporting_sources: List[str]
    confidence: float


class CostTracker(BaseModel):
    """成本追踪"""
    llm_calls: int = 0
    search_calls: int = 0
    tokens_input: int = 0
    tokens_output: int = 0
    estimated_cost: float = 0.0


class ResearchRequest(BaseModel):
    """研究请求"""
    topic: str = Field(..., min_length=5, description="研究主题")
    depth: str = Field(default="standard", description="研究深度 (quick/standard/deep)")
    custom_instructions: Optional[str] = Field(default=None, description="自定义指令")


class ResearchResponse(BaseModel):
    """研究响应"""
    session_id: str
    status: str
    message: str


class ResearchStatus(BaseModel):
    """研究状态"""
    session_id: str
    status: str
    progress: int
    stage: str
    current_action: str
    report: Optional[str] = None
    sources: Optional[List[Dict[str, Any]]] = None
    cost_estimate: Optional[float] = None
    error_message: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
