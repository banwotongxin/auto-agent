# 自动化深度研究智能体 - 技术执行计划文档

## 项目概述

**项目名称**: AutoResearch Agent (自动化深度研究智能体)  
**框架选择**: LangGraph (基于状态管理优势)  
**核心目标**: 接收研究主题 → 自动搜索收集 → 分析综合 → 生成结构化研究报告

---

## 系统架构设计

### 1.1 整体架构

```
┌─────────────────────────────────────────────────────────────────┐
│                        应用展示层                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │ Web界面      │  │ REST API     │  │ WebSocket进度推送    │  │
│  │ (React)      │  │ (FastAPI)    │  │                      │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────────┐
│                       智能体编排层 (LangGraph)                   │
│                                                                  │
│  ┌────────────┐   ┌────────────┐   ┌────────────┐   ┌────────┐ │
│  │ 规划节点   │──▶│ 收集节点   │──▶│ 分析节点   │──▶│报告节点│ │
│  │ (Planner)  │   │ (Searcher) │   │ (Analyzer) │   │ (Gen)  │ │
│  └────────────┘   └────────────┘   └────────────┘   └────────┘ │
│        │                │                │              │      │
│        ▼                ▼                ▼              ▼      │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │              状态管理 (State Graph)                      │ │
│  │  - 研究会话状态                                          │ │
│  │  - 中间结果缓存                                          │ │
│  │  - 决策路由                                              │ │
│  └──────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────────┐
│                        工具服务层                                │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────────────┐  │
│  │ 搜索服务 │  │ 网页解析 │  │ 向量存储 │  │ LLM推理服务    │  │
│  │ Tavily   │  │ FireCrawl│  │ ChromaDB │  │ Claude/GPT     │  │
│  └──────────┘  └──────────┘  └──────────┘  └────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 LangGraph状态设计

```python
class ResearchState(TypedDict):
    # 输入
    topic: str                          # 研究主题
    depth: str                          # 研究深度: quick/standard/deep
    
    # 规划阶段
    plan: ResearchPlan                  # 研究计划
    search_queries: List[str]           # 搜索关键词列表
    
    # 收集阶段
    search_results: List[SearchResult]  # 原始搜索结果
    collected_sources: List[Source]     # 筛选后的资料源
    
    # 分析阶段
    key_findings: List[Finding]         # 关键发现
    analysis_notes: List[Note]          # 分析笔记
    knowledge_graph: Dict               # 知识图谱
    
    # 生成阶段
    report_sections: List[Section]      # 报告章节
    final_report: str                   # 最终报告
    
    # 元信息
    session_id: str
    created_at: datetime
    cost_tracker: CostTracker
    error_log: List[str]
```

---

## 第一阶段：基础框架搭建 (Week 1)

### 2.1 项目结构初始化

```
auto-research-agent/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI入口
│   ├── config.py                  # 全局配置
│   │
│   ├── core/                      # 核心组件
│   │   ├── __init__.py
│   │   ├── state.py               # LangGraph状态定义
│   │   ├── graph.py               # 工作流图构建
│   │   └── nodes/                 # 工作流节点
│   │       ├── __init__.py
│   │       ├── planner.py         # 规划节点
│   │       ├── searcher.py        # 收集节点
│   │       ├── analyzer.py        # 分析节点
│   │       ├── generator.py       # 报告生成节点
│   │       └── quality.py         # 质量控制节点
│   │
│   ├── services/                  # 服务层
│   │   ├── __init__.py
│   │   ├── llm.py                 # LLM服务封装
│   │   ├── search.py              # 搜索服务
│   │   ├── parser.py              # 网页解析服务
│   │   └── vector_store.py        # 向量存储服务
│   │
│   ├── models/                    # 数据模型
│   │   ├── __init__.py
│   │   ├── schemas.py             # Pydantic模型
│   │   └── enums.py               # 枚举定义
│   │
│   ├── api/                       # API路由
│   │   ├── __init__.py
│   │   ├── routes.py              # REST端点
│   │   └── websocket.py           # WebSocket端点
│   │
│   └── utils/                     # 工具函数
│       ├── __init__.py
│       ├── logger.py              # 日志配置
│       └── cost_tracker.py        # 成本追踪
│
├── frontend/                      # React前端
│   ├── src/
│   ├── public/
│   └── package.json
│
├── tests/                         # 测试
│   ├── unit/
│   ├── integration/
│   └── conftest.py
│
├── docs/                          # 文档
├── notebooks/                     # Jupyter笔记本
├── docker/                        # Docker配置
├── .env.example                   # 环境变量示例
├── requirements.txt               # Python依赖
├── pyproject.toml                 # 项目配置
└── README.md
```

### 2.2 依赖配置 (requirements.txt)

```
# Web框架
fastapi==0.115.0
uvicorn[standard]==0.32.0
websockets==13.1

# LangChain & LangGraph
langchain==0.3.0
langchain-openai==0.2.0
langchain-anthropic==0.2.0
langgraph==0.2.0

# 搜索和解析
tavily-python==0.5.0
firecrawl-py==1.5.0
beautifulsoup4==4.12.0
requests==2.32.0

# 向量存储和NLP
chromadb==0.5.0
sentence-transformers==3.0.0
numpy==1.26.0

# 数据验证和工具
pydantic==2.9.0
pydantic-settings==2.5.0
python-dotenv==1.0.0
httpx==0.27.0

# 异步和任务队列
celery==5.4.0
redis==5.0.0

# 日志和监控
structlog==24.4.0
prometheus-client==0.21.0

# 测试
pytest==8.3.0
pytest-asyncio==0.24.0
pytest-cov==5.0.0
httpx==0.27.0

# 开发工具
black==24.8.0
isort==5.13.0
mypy==1.11.0
```

### 2.3 核心配置 (config.py)

```python
from pydantic_settings import BaseSettings
from typing import List, Optional

class Settings(BaseSettings):
    # 应用配置
    APP_NAME: str = "AutoResearch Agent"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # API配置
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_WORKERS: int = 1
    
    # LLM配置
    DEFAULT_LLM_PROVIDER: str = "anthropic"  # anthropic/openai
    ANTHROPIC_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    DEFAULT_MODEL: str = "claude-3-sonnet-20240229"
    MAX_TOKENS: int = 4000
    TEMPERATURE: float = 0.3
    
    # 搜索配置
    TAVILY_API_KEY: Optional[str] = None
    MAX_SEARCH_RESULTS: int = 10
    SEARCH_DEPTH: str = "advanced"  # basic/advanced
    
    # 网页解析配置
    FIRECRAWL_API_KEY: Optional[str] = None
    REQUEST_TIMEOUT: int = 30
    MAX_CONTENT_LENGTH: int = 100000
    
    # 向量存储配置
    CHROMA_PERSIST_DIR: str = "./chroma_db"
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    
    # 研究配置
    MAX_RESEARCH_DEPTH: int = 3
    MAX_SEARCH_QUERIES: int = 15
    MIN_SOURCE_QUALITY: float = 0.6
    
    # Redis配置（任务队列）
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # 成本控制
    MAX_COST_PER_RESEARCH: float = 5.0  # 美元
    ENABLE_COST_TRACKING: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
```

### 2.4 状态模型定义 (core/state.py)

```python
from typing import TypedDict, List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum

class ResearchStage(str, Enum):
    PLANNING = "planning"
    SEARCHING = "searching"
    ANALYZING = "analyzing"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"

class ResearchDepth(str, Enum):
    QUICK = "quick"        # 1轮搜索，5-10个来源
    STANDARD = "standard"  # 2轮搜索，15-20个来源
    DEEP = "deep"          # 3轮搜索，30+个来源

@dataclass
class SearchResult:
    url: str
    title: str
    content: str
    snippet: str
    score: float
    source_type: str = "web"
    credibility_score: float = 0.5
    extracted_at: datetime = field(default_factory=datetime.now)

@dataclass
class Source:
    url: str
    title: str
    content: str
    relevance_score: float
    credibility_score: float
    key_points: List[str] = field(default_factory=list)

@dataclass
class ResearchPlan:
    topic: str
    sub_questions: List[str]
    search_strategy: Dict[str, Any]
    expected_outputs: List[str]
    estimated_cost: float

@dataclass
class Finding:
    topic: str
    content: str
    supporting_sources: List[str]
    confidence: float

@dataclass
class CostTracker:
    llm_calls: int = 0
    search_calls: int = 0
    tokens_input: int = 0
    tokens_output: int = 0
    estimated_cost: float = 0.0

# LangGraph State定义
class ResearchState(TypedDict):
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
    
    # 控制信息
    iteration_count: int
    cost_tracker: Dict[str, Any]
    error_messages: List[str]
    should_continue: bool
```

### 2.5 LangGraph基础工作流 (core/graph.py)

```python
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
    """创建研究工作流图"""
    
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
    
    # 添加边和条件路由
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
    
    # 编译图
    memory = MemorySaver()
    return workflow.compile(checkpointer=memory)
```

---

## 第二阶段：核心功能实现 (Week 2-3)

### 3.1 任务规划节点 (nodes/planner.py)

```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from app.core.state import ResearchState
from app.services.llm import get_llm
from app.config import settings

PLANNING_PROMPT = """你是一个专业的研究规划专家。你的任务是分析用户的研究主题，制定详细的研究计划。

研究主题: {topic}
研究深度: {depth}

请生成以下JSON格式的研究计划:
{{
    "topic": "原始主题",
    "sub_questions": ["分解后的子问题1", "子问题2", ...],
    "search_queries": ["搜索关键词1", "搜索关键词2", ...],
    "search_strategy": {{
        "rounds": 搜索轮数,
        "sources_per_round": 每轮来源数,
        "focus_areas": ["重点关注领域"]
    }},
    "expected_outputs": ["预期产出1", "预期产出2"],
    "estimated_time_minutes": 预计时间
}}

要求:
1. 子问题要覆盖主题的各个维度
2. 搜索关键词要多样化，覆盖不同角度
3. 搜索策略要与深度级别匹配
4. 只返回JSON，不要其他内容
"""

async def planning_node(state: ResearchState) -> ResearchState:
    """规划节点：分解研究主题，制定搜索策略"""
    
    llm = get_llm()
    prompt = ChatPromptTemplate.from_template(PLANNING_PROMPT)
    parser = JsonOutputParser()
    
    chain = prompt | llm | parser
    
    result = await chain.ainvoke({
        "topic": state["topic"],
        "depth": state["depth"]
    })
    
    # 更新状态
    state["plan"] = result
    state["search_queries"] = result.get("search_queries", [])
    state["stage"] = "searching"
    
    return state
```

### 3.2 信息收集节点 (nodes/searcher.py)

```python
import asyncio
from typing import List
from app.core.state import ResearchState, SearchResult, Source
from app.services.search import SearchService
from app.services.parser import WebParser
from app.config import settings

class SearchNode:
    def __init__(self):
        self.search_service = SearchService()
        self.parser = WebParser()
    
    async def search_and_parse(self, query: str) -> List[Source]:
        """搜索并解析单个查询"""
        # 执行搜索
        results = await self.search_service.search(
            query=query,
            max_results=settings.MAX_SEARCH_RESULTS // len(queries)
        )
        
        sources = []
        for result in results:
            try:
                # 解析网页内容
                content = await self.parser.parse(result.url)
                
                # 计算相关性分数
                relevance = self._calculate_relevance(content, query)
                credibility = self._assess_credibility(result.url)
                
                if relevance >= settings.MIN_SOURCE_QUALITY:
                    source = Source(
                        url=result.url,
                        title=result.title,
                        content=content,
                        relevance_score=relevance,
                        credibility_score=credibility
                    )
                    sources.append(source)
                    
            except Exception as e:
                continue
        
        return sources
    
    async def execute(self, state: ResearchState) -> ResearchState:
        """搜索节点主逻辑"""
        queries = state["search_queries"]
        
        # 并行执行多个搜索
        tasks = [self.search_and_parse(q) for q in queries]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 合并和去重结果
        all_sources = []
        seen_urls = set()
        
        for sources in results:
            if isinstance(sources, Exception):
                continue
            for source in sources:
                if source.url not in seen_urls:
                    all_sources.append(source)
                    seen_urls.add(source.url)
        
        # 按综合分数排序
        all_sources.sort(
            key=lambda x: x.relevance_score * 0.7 + x.credibility_score * 0.3,
            reverse=True
        )
        
        # 限制来源数量
        max_sources = {"quick": 10, "standard": 20, "deep": 35}[state["depth"]]
        state["sources"] = [s.__dict__ for s in all_sources[:max_sources]]
        state["stage"] = "analyzing"
        
        return state
```

### 3.3 搜索服务 (services/search.py)

```python
from tavily import TavilyClient
from typing import List, Dict, Any
from app.config import settings

class SearchService:
    def __init__(self):
        self.client = TavilyClient(api_key=settings.TAVILY_API_KEY)
    
    async def search(
        self,
        query: str,
        max_results: int = 10,
        search_depth: str = "advanced",
        include_answer: bool = False
    ) -> List[Dict[str, Any]]:
        """
        执行 Tavily 搜索
        
        Args:
            query: 搜索查询
            max_results: 最大结果数
            search_depth: basic 或 advanced
        """
        try:
            response = self.client.search(
                query=query,
                max_results=max_results,
                search_depth=search_depth,
                include_answer=include_answer,
                include_raw_content=True
            )
            
            results = []
            for item in response.get("results", []):
                results.append({
                    "url": item.get("url"),
                    "title": item.get("title"),
                    "content": item.get("content", ""),
                    "score": item.get("score", 0),
                    "raw_content": item.get("raw_content", "")
                })
            
            return results
            
        except Exception as e:
            raise SearchError(f"Search failed: {str(e)}")

class SearchError(Exception):
    pass
```

### 3.4 分析综合节点 (nodes/analyzer.py)

```python
from langchain_core.prompts import ChatPromptTemplate
from typing import List
from app.core.state import ResearchState, Finding
from app.services.llm import get_llm
from app.services.vector_store import VectorStore

ANALYSIS_PROMPT = """基于以下研究资料，提取关键发现并进行分析。

研究主题: {topic}

资料内容:
{sources_text}

请完成以下分析:
1. 提取5-10个关键发现，每个发现包含主题、内容和支持来源
2. 识别信息中的主要观点、争议点和共识
3. 评估每个发现的可信度
4. 指出信息缺口和需要进一步研究的问题

以JSON格式返回:
{{
    "findings": [
        {{
            "topic": "发现主题",
            "content": "详细内容",
            "supporting_sources": ["url1", "url2"],
            "confidence": 0.0-1.0
        }}
    ],
    "key_themes": ["主题1", "主题2"],
    "gaps": ["信息缺口1", "缺口2"],
    "summary": "整体分析摘要"
}}
"""

class AnalysisNode:
    def __init__(self):
        self.vector_store = VectorStore()
        self.llm = get_llm()
    
    async def execute(self, state: ResearchState) -> ResearchState:
        """分析节点主逻辑"""
        
        # 1. 将来源存入向量数据库
        await self.vector_store.add_sources(state["sources"])
        
        # 2. 准备分析输入
        sources_text = self._format_sources(state["sources"])
        
        # 3. 执行LLM分析
        prompt = ChatPromptTemplate.from_template(ANALYSIS_PROMPT)
        chain = prompt | self.llm
        
        response = await chain.ainvoke({
            "topic": state["topic"],
            "sources_text": sources_text[:15000]  # 限制长度
        })
        
        # 4. 解析结果
        analysis_result = self._parse_analysis(response.content)
        
        # 5. 更新状态
        state["findings"] = analysis_result.get("findings", [])
        state["analysis_summary"] = analysis_result.get("summary", "")
        state["stage"] = "generating"
        
        return state
```

### 3.5 报告生成节点 (nodes/generator.py)

```python
from langchain_core.prompts import ChatPromptTemplate
from app.core.state import ResearchState
from app.services.llm import get_llm

REPORT_PROMPT = """基于以下分析结果，生成一份专业的研究报告。

研究主题: {topic}

关键发现:
{findings}

分析摘要:
{summary}

来源数量: {source_count}

请生成一份结构化的Markdown格式研究报告，包含以下部分:

# {topic}

## 执行摘要
- 研究背景和目的
- 主要发现概述
- 核心结论

## 研究背景
- 主题介绍
- 研究范围

## 核心发现
### [发现主题1]
详细分析...

### [发现主题2]
...

## 详细分析
- 按子主题深入分析
- 引用支持性证据

## 结论与建议
- 主要结论
- 实际应用建议
- 未来研究方向

## 参考来源
- 列出所有引用的来源

要求:
- 使用专业的学术写作风格
- 适当使用小标题组织内容
- 在关键观点后标注来源引用
- 报告长度根据深度级别调整
"""

class GeneratorNode:
    def __init__(self):
        self.llm = get_llm()
    
    async def execute(self, state: ResearchState) -> ResearchState:
        """报告生成节点主逻辑"""
        
        findings_text = self._format_findings(state["findings"])
        
        prompt = ChatPromptTemplate.from_template(REPORT_PROMPT)
        chain = prompt | self.llm
        
        response = await chain.ainvoke({
            "topic": state["topic"],
            "findings": findings_text,
            "summary": state.get("analysis_summary", ""),
            "source_count": len(state["sources"])
        })
        
        # 生成报告
        state["final_report"] = response.content
        state["stage"] = "quality_check"
        
        return state
```

---

## 第三阶段：智能优化 (Week 4)

### 4.1 质量控制节点 (nodes/quality.py)

```python
from app.core.state import ResearchState
from typing import Literal

class QualityController:
    """质量控制控制器"""
    
    def check_report_quality(self, state: ResearchState) -> dict:
        """检查报告质量"""
        checks = {
            "has_content": self._check_content(state),
            "source_coverage": self._check_source_coverage(state),
            "structure_ok": self._check_structure(state),
            "sufficient_depth": self._check_depth(state)
        }
        
        return {
            "passed": all(checks.values()),
            "checks": checks,
            "recommendation": self._get_recommendation(checks, state)
        }
    
    def _check_content(self, state: ResearchState) -> bool:
        """检查内容完整性"""
        report = state.get("final_report", "")
        return len(report) > 2000 and "执行摘要" in report
    
    def _check_source_coverage(self, state: ResearchState) -> bool:
        """检查来源引用情况"""
        report = state.get("final_report", "")
        sources = state.get("sources", [])
        
        # 检查是否有足够来源被引用
        cited_count = sum(1 for s in sources if s.get("url", "") in report)
        return cited_count >= len(sources) * 0.3  # 至少30%来源被引用
    
    def _get_recommendation(
        self,
        checks: dict,
        state: ResearchState
    ) -> Literal["completed", "needs_more_search", "needs_reanalysis"]:
        """基于检查结果给出建议"""
        
        if all(checks.values()):
            return "completed"
        
        if not checks.get("source_coverage", True):
            return "needs_more_search"
        
        if not checks.get("structure_ok", True):
            return "needs_reanalysis"
        
        return "completed"

def route_decision(state: ResearchState) -> str:
    """路由决策函数"""
    
    # 检查迭代次数
    if state.get("iteration_count", 0) >= 3:
        return "completed"
    
    # 检查错误
    if state.get("error_messages"):
        return "failed"
    
    # 质量控制检查
    controller = QualityController()
    quality_check = controller.check_report_quality(state)
    
    if quality_check["passed"]:
        return "completed"
    
    return quality_check["recommendation"]
```

### 4.2 自适应搜索策略

```python
class AdaptiveSearchStrategy:
    """自适应搜索策略 - 根据初步结果动态调整搜索方向"""
    
    def __init__(self, llm):
        self.llm = llm
    
    async def refine_queries(
        self,
        original_queries: List[str],
        initial_results: List[Dict],
        gaps: List[str]
    ) -> List[str]:
        """
        基于初步搜索结果，生成补充查询
        
        策略:
        1. 识别信息缺口
        2. 针对热门子话题深入
        3. 寻找对立观点
        4. 补充权威来源
        """
        
        prompt = f"""基于初步搜索结果，识别信息缺口并生成补充搜索查询。

原始查询: {original_queries}
初步结果数量: {len(initial_results)}
已识别缺口: {gaps}

请生成3-5个补充搜索查询，用于：
1. 填补信息缺口
2. 深入热门子话题
3. 寻找不同观点
4. 补充权威来源

只返回查询列表，每行一个。"""
        
        response = await self.llm.ainvoke(prompt)
        new_queries = [q.strip() for q in response.content.split('\n') if q.strip()]
        
        return new_queries
```

---

## 第四阶段：服务化和界面 (Week 5-6)

### 5.1 FastAPI API端点 (api/routes.py)

```python
from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List
import uuid

router = APIRouter(prefix="/api/v1/research", tags=["research"])

class ResearchRequest(BaseModel):
    topic: str
    depth: str = "standard"  # quick, standard, deep
    custom_instructions: Optional[str] = None

class ResearchResponse(BaseModel):
    session_id: str
    status: str
    message: str

class ResearchResult(BaseModel):
    session_id: str
    status: str
    progress: int
    report: Optional[str]
    sources: Optional[List[dict]]
    cost_estimate: Optional[float]

# 会话存储（生产环境使用Redis）
sessions = {}

@router.post("/start", response_model=ResearchResponse)
async def start_research(request: ResearchRequest):
    """启动新的研究任务"""
    session_id = str(uuid.uuid4())
    
    # 初始化研究会话
    sessions[session_id] = {
        "session_id": session_id,
        "topic": request.topic,
        "depth": request.depth,
        "status": "initialized",
        "progress": 0,
        "result": None
    }
    
    # 启动异步研究任务
    from app.core.worker import run_research_task
    asyncio.create_task(run_research_task(session_id, request))
    
    return ResearchResponse(
        session_id=session_id,
        status="initialized",
        message="Research task started"
    )

@router.get("/{session_id}/status", response_model=ResearchResult)
async def get_research_status(session_id: str):
    """获取研究任务状态"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[session_id]
    return ResearchResult(
        session_id=session_id,
        status=session["status"],
        progress=session.get("progress", 0),
        report=session.get("result", {}).get("report"),
        sources=session.get("result", {}).get("sources"),
        cost_estimate=session.get("result", {}).get("cost")
    )

@router.get("/{session_id}/stream")
async def stream_research_progress(session_id: str):
    """WebSocket风格的SSE流，实时推送进度"""
    
    async def event_generator():
        while True:
            if session_id not in sessions:
                yield f"data: {{'error': 'Session not found'}}\n\n"
                break
            
            session = sessions[session_id]
            yield f"data: {json.dumps(session)}\n\n"
            
            if session["status"] in ["completed", "failed"]:
                break
            
            await asyncio.sleep(1)
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )
```

### 5.2 WebSocket实时通信 (api/websocket.py)

```python
from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict
import json

class ConnectionManager:
    """WebSocket连接管理器"""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, session_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[session_id] = websocket
    
    def disconnect(self, session_id: str):
        if session_id in self.active_connections:
            del self.active_connections[session_id]
    
    async def send_progress(self, session_id: str, data: dict):
        if session_id in self.active_connections:
            await self.active_connections[session_id].send_json(data)

manager = ConnectionManager()

@router.websocket("/ws/{session_id}")
async def research_websocket(websocket: WebSocket, session_id: str):
    await manager.connect(session_id, websocket)
    
    try:
        while True:
            # 接收心跳或控制命令
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get("action") == "get_status":
                # 发送当前状态
                if session_id in sessions:
                    await manager.send_progress(session_id, sessions[session_id])
                    
    except WebSocketDisconnect:
        manager.disconnect(session_id)
```

### 5.3 React前端组件结构

```typescript
// 核心组件
src/
├── components/
│   ├── ResearchForm.tsx        # 研究主题输入表单
│   ├── ProgressTracker.tsx     # 进度追踪组件
│   ├── ReportViewer.tsx        # 报告展示组件
│   ├── SourceList.tsx          # 来源列表组件
│   └── CostEstimator.tsx       # 成本估算组件
├── hooks/
│   ├── useResearch.ts          # 研究任务管理Hook
│   ├── useWebSocket.ts         # WebSocket连接Hook
│   └── useStreamingReport.ts   # 流式报告接收Hook
├── pages/
│   ├── Home.tsx                # 首页
│   └── Research.tsx            # 研究任务页面
└── services/
    ├── api.ts                  # API服务
    └── websocket.ts            # WebSocket服务
```

---

## 第五阶段：测试和优化 (Week 7)

### 6.1 测试策略

```
测试覆盖:
├── 单元测试 (60%)
│   ├── 测试每个工作流节点的独立逻辑
│   ├── 测试服务层的API调用
│   └── 测试工具函数
│
├── 集成测试 (30%)
│   ├── 测试完整研究工作流
│   ├── 测试API端点
│   └── 测试服务间交互
│
└── 端到端测试 (10%)
    └── 测试完整用户场景
```

### 6.2 关键测试用例

```python
# tests/integration/test_research_workflow.py

import pytest
from app.core.graph import create_research_graph
from app.core.state import ResearchState

@pytest.mark.asyncio
async def test_research_workflow_complete():
    """测试完整研究工作流"""
    
    # 准备初始状态
    initial_state: ResearchState = {
        "session_id": "test-001",
        "topic": "人工智能在医疗诊断中的应用",
        "depth": "quick",
        "stage": "planning",
        "created_at": "2024-01-01T00:00:00",
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
        "cost_tracker": {},
        "error_messages": [],
        "should_continue": True
    }
    
    # 执行工作流
    graph = create_research_graph()
    result = await graph.ainvoke(initial_state)
    
    # 验证结果
    assert result["final_report"] is not None
    assert len(result["sources"]) > 0
    assert result["stage"] == "completed"

# tests/unit/test_search_service.py

@pytest.mark.asyncio
async def test_search_service(mock_tavily_client):
    """测试搜索服务"""
    service = SearchService()
    
    results = await service.search("test query", max_results=5)
    
    assert isinstance(results, list)
    assert len(results) <= 5
    assert all("url" in r for r in results)
```

### 6.3 性能指标

| 指标 | 目标值 | 测试方法 |
|------|--------|----------|
| 任务完成率 | >95% | 运行100个测试任务 |
| 平均响应时间 | <30秒 (Quick) | 基准测试 |
| Token效率 | <5000 tokens/query | 成本分析 |
| 来源质量分 | >0.7 | 人工评分抽样 |

---

## 执行检查清单

### Week 1 检查点
- [ ] 项目结构创建完成
- [ ] 依赖安装成功
- [ ] LangGraph基础工作流可运行
- [ ] 配置文件和环境变量设置正确
- [ ] 基础日志系统工作正常

### Week 2-3 检查点
- [ ] 规划节点能正确分解主题
- [ ] 搜索节点能收集来源
- [ ] 分析节点能提取关键发现
- [ ] 报告节点能生成完整报告
- [ ] 完整工作流跑通示例任务

### Week 4 检查点
- [ ] 质量控制系统集成
- [ ] 自适应搜索策略工作
- [ ] 错误处理和重试机制
- [ ] 成本追踪准确

### Week 5-6 检查点
- [ ] FastAPI服务启动正常
- [ ] 所有API端点测试通过
- [ ] WebSocket实时推送工作
- [ ] React前端界面可用
- [ ] 前后端集成测试通过

### Week 7 检查点
- [ ] 单元测试覆盖率>60%
- [ ] 集成测试通过
- [ ] 性能测试达标
- [ ] 文档编写完成
- [ ] 示例和教程可用

---

## 下一步行动

现在开始 **第一阶段：基础框架搭建**，请确认后继续执行代码生成。
