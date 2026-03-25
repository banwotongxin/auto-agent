<<<<<<< HEAD
# AutoResearch Agent - 自动化深度研究智能体

基于LangGraph构建的自动化深度研究智能体，能够接收研究主题后自动执行信息搜索、分析、综合和报告生成全流程。

## 项目特性

- **智能规划**: 自动分解研究主题，制定搜索策略
- **深度搜索**: 并行执行多轮搜索，智能过滤高质量来源
- **分析综合**: 向量存储支持，提取关键发现和洞察
- **报告生成**: 生成结构化Markdown研究报告
- **质量控制**: 自适应迭代优化，确保研究质量
- **实时反馈**: WebSocket/SSE实时推送研究进度

## 技术栈

- **Agent框架**: LangGraph
- **LLM**: Claude / GPT
- **搜索**: Tavily API
- **向量存储**: ChromaDB
- **后端**: FastAPI
- **前端**: React (可选)

## 快速开始

### 1. 安装依赖

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
cp .env.example .env
```

编辑 `.env` 文件，配置以下必需的环境变量：

```env
# LLM配置（至少配置一个）
ANTHROPIC_API_KEY=your_anthropic_api_key
OPENAI_API_KEY=your_openai_api_key

# 搜索配置
TAVILY_API_KEY=your_tavily_api_key
```

获取API密钥：
- [Anthropic API](https://console.anthropic.com/)
- [OpenAI API](https://platform.openai.com/)
- [Tavily API](https://tavily.com/)

### 3. 启动服务

```bash
# 开发模式
python -m app.main

# 或使用uvicorn
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

服务启动后，访问 http://localhost:8000/docs 查看API文档。

## API使用

### 启动研究任务

```bash
curl -X POST "http://localhost:8000/api/v1/research/start" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "人工智能在医疗诊断中的应用",
    "depth": "standard"
  }'
```

响应：
```json
{
  "session_id": "uuid-string",
  "status": "initialized",
  "message": "Research task started successfully"
}
```

### 查询任务状态

```bash
curl "http://localhost:8000/api/v1/research/{session_id}/status"
```

### 流式获取进度

```bash
curl "http://localhost:8000/api/v1/research/{session_id}/stream"
```

## 研究深度级别

- **quick**: 快速模式，1轮搜索，5-10个来源，约5-10分钟
- **standard**: 标准模式，2轮搜索，15-20个来源，约15-20分钟
- **deep**: 深度模式，3轮搜索，30+个来源，约30-45分钟

## 项目结构

```
auto-research-agent/
├── app/
│   ├── core/              # 核心工作流
│   │   ├── nodes/         # LangGraph节点
│   │   ├── graph.py       # 工作流图
│   │   └── state.py       # 状态定义
│   ├── services/          # 服务层
│   │   ├── llm.py         # LLM服务
│   │   ├── search.py      # 搜索服务
│   │   ├── parser.py      # 网页解析
│   │   └── vector_store.py # 向量存储
│   ├── api/               # API路由
│   ├── models/            # 数据模型
│   └── utils/             # 工具函数
├── tests/                 # 测试
├── docs/                  # 文档
└── README.md
```

## 系统架构

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   用户界面   │───▶│  FastAPI    │───▶│ LangGraph   │
│   (React)   │◀───│   服务      │◀───│  工作流     │
└─────────────┘    └─────────────┘    └──────┬──────┘
                                              │
                    ┌─────────────────────────┼─────────────────────────┐
                    │                         │                         │
                    ▼                         ▼                         ▼
              ┌──────────┐            ┌──────────┐            ┌──────────┐
              │  搜索    │            │  LLM     │            │  向量    │
              │  Tavily  │            │ Claude   │            │ ChromaDB │
              └──────────┘            └──────────┘            └──────────┘
```

## 工作流节点

1. **Planner** (规划节点): 分解主题，制定搜索策略
2. **Searcher** (收集节点): 并行搜索，解析内容，过滤来源
3. **Analyzer** (分析节点): 提取关键发现，识别趋势
4. **Generator** (生成节点): 生成结构化研究报告
5. **Quality** (质量节点): 质量检查，路由决策

## 成本控制

系统提供成本追踪功能：

- LLM调用成本估算
- 搜索API调用统计
- 总成本预算控制

在 `.env` 中配置：
```env
MAX_COST_PER_RESEARCH=5.0  # 单次研究最大成本（美元）
ENABLE_COST_TRACKING=true
```

## 测试

```bash
# 运行所有测试
pytest

# 运行单元测试
pytest tests/unit/

# 运行集成测试
pytest tests/integration/

# 生成覆盖率报告
pytest --cov=app --cov-report=html
```

## 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 许可证

MIT License

## 致谢

- [LangGraph](https://github.com/langchain-ai/langgraph)
- [LangChain](https://github.com/langchain-ai/langchain)
- [Tavily](https://tavily.com/)
- [ChromaDB](https://www.trychroma.com/)
=======
# auto-agent
自动深度研究智能体
>>>>>>> 61b4a23c97f74ee7c89e20ca4397760f3d85bd2b
