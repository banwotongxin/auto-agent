"""枚举定义

自动深度研究智能体中使用的枚举类型定义。
"""
from enum import Enum


class ResearchStage(str, Enum):
    """研究阶段枚举
    
    定义研究工作流的各个阶段。
    """
    INITIALIZED = "initialized"  # 初始化
    PLANNING = "planning"  # 规划阶段
    SEARCHING = "searching"  # 搜索收集阶段
    ANALYZING = "analyzing"  # 分析阶段
    GENERATING = "generating"  # 报告生成阶段
    QUALITY_CHECK = "quality_check"  # 质量检查阶段
    COMPLETED = "completed"  # 已完成
    FAILED = "failed"  # 失败


class ResearchDepth(str, Enum):
    """
    研究深度级别枚举
    
    定义研究的深度级别，影响搜索轮数、来源数量和报告长度。
    """
    QUICK = "quick"  # 快速模式：1轮搜索，5-10个来源，约1500字
    STANDARD = "standard"  # 标准模式：2轮搜索，15-20个来源，约3000字
    DEEP = "deep"  # 深度模式：3轮搜索，30+个来源，约5000字


class SourceType(str, Enum):
    """
    来源类型枚举
    
    定义信息来源的类型。
    """
    WEB = "web"  # 普通网页
    ACADEMIC = "academic"  # 学术来源 (.edu, arxiv, IEEE等)
    NEWS = "news"  # 新闻来源
    BLOG = "blog"  # 博客来源
    WIKI = "wiki"  # 百科全书 (Wikipedia)
    SOCIAL = "social"  # 社交媒体
    OFFICIAL = "official"  # 官方机构 (政府、组织)
    PROFESSIONAL = "professional"  # 专业机构
    OTHER = "other"  # 其他


class QualityLevel(str, Enum):
    """
    质量等级枚举
    
    用于评估来源和研究的质量等级。
    """
    HIGH = "high"  # 高质量 (> 0.8)
    MEDIUM = "medium"  # 中等质量 (0.5 - 0.8)
    LOW = "low"  # 低质量 (< 0.5)


class LLMProvider(str, Enum):
    """LLM提供商枚举"""
    ANTHROPIC = "anthropic"  # Anthropic (Claude)
    OPENAI = "openai"  # OpenAI (GPT)


class RouteDecision(str, Enum):
    """
    路由决策枚举
    
    定义质量检查后的路由决策。
    """
    COMPLETED = "completed"  # 研究完成
    NEEDS_MORE_SEARCH = "needs_more_search"  # 需要更多搜索
    NEEDS_REANALYSIS = "needs_reanalysis"  # 需要重新分析
    FAILED = "failed"  # 研究失败


class EvidenceStrength(str, Enum):
    """
    证据强度枚举
    
    用于评估研究发现的可信度。
    """
    STRONG = "strong"  # 强证据：有多个高质量来源支持
    MODERATE = "moderate"  # 中等证据：有来源支持但可能存在争议
    WEAK = "weak"  # 弱证据：来源有限或质量较低
