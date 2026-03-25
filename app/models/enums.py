"""枚举定义"""
from enum import Enum


class ResearchStage(str, Enum):
    """研究阶段"""
    INITIALIZED = "initialized"
    PLANNING = "planning"
    SEARCHING = "searching"
    ANALYZING = "analyzing"
    GENERATING = "generating"
    QUALITY_CHECK = "quality_check"
    COMPLETED = "completed"
    FAILED = "failed"


class ResearchDepth(str, Enum):
    """研究深度级别"""
    QUICK = "quick"           # 快速模式：1轮搜索，5-10个来源
    STANDARD = "standard"     # 标准模式：2轮搜索，15-20个来源
    DEEP = "deep"             # 深度模式：3轮搜索，30+个来源


class SourceType(str, Enum):
    """来源类型"""
    WEB = "web"
    ACADEMIC = "academic"
    NEWS = "news"
    BLOG = "blog"
    WIKI = "wiki"
    OTHER = "other"


class QualityLevel(str, Enum):
    """质量等级"""
    HIGH = "high"             # > 0.8
    MEDIUM = "medium"         # 0.5 - 0.8
    LOW = "low"               # < 0.5


class LLMProvider(str, Enum):
    """LLM提供商"""
    ANTHROPIC = "anthropic"
    OPENAI = "openai"
