# AutoResearch Agent - 自动化深度研究智能体

基于LangGraph构建的自动化深度研究智能体，能够接收研究主题后自动执行信息搜索、分析、综合和报告生成全流程。

## 项目特性

- **智能规划**: 自动分解研究主题，制定多维度搜索策略
- **深度搜索**: 并行执行多轮搜索，智能过滤高质量来源
- **分析综合**: 向量存储支持，提取关键发现、识别共识与分歧
- **报告生成**: 生成结构化Markdown研究报告，支持多种深度级别
- **质量控制**: 多阶段质量检查，自适应迭代优化
- **实时反馈**: WebSocket/SSE实时推送研究进度

## 技术栈

- **Agent框架**: LangGraph
- **LLM**: Claude / GPT (支持Anthropic和OpenAI)
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

| 级别 | 搜索轮数 | 来源数量 | 报告长度 | 预估时间 |
|------|---------|---------|---------|---------|
| **quick** | 1轮 | 5-10个 | ~1500字 | 5-10分钟 |
| **standard** | 2轮 | 15-20个 | ~3000字 | 15-20分钟 |
| **deep** | 3轮 | 30+个 | ~5000字 | 30-45分钟 |

## 项目结构

```
auto-agent/
├── app/
│   ├── api/
│   │   ├── routes.py       # REST API路由
│   │   └── websocket.py    # WebSocket通信
│   ├── core/
│   │   ├── nodes/          # LangGraph工作流节点
│   │   │   ├── planner.py  # 规划节点
│   │   │   ├── searcher.py # 搜索节点
│   │   │   ├── analyzer.py # 分析节点
│   │   │   ├── generator.py # 生成节点
│   │   │   └── quality.py  # 质量控制节点
│   │   ├── graph.py        # 工作流图定义
│   │   └── state.py        # 状态定义
│   ├── models/
│   │   ├── enums.py        # 枚举定义
│   │   └── schemas.py      # Pydantic数据模型
│   ├── services/
│   │   ├── llm.py          # LLM服务
│   │   ├── search.py       # 搜索服务
│   │   ├── parser.py       # 网页解析
│   │   └── vector_store.py # 向量存储
│   ├── utils/
│   │   ├── logger.py       # 日志配置
│   │   └── cost_tracker.py # 成本追踪
│   ├── config.py           # 全局配置
│   └── main.py             # 应用入口
├── tests/
│   ├── conftest.py         # pytest配置
│   ├── unit/               # 单元测试
│   └── integration/        # 集成测试
├── frontend/               # 前端应用
├── run.py                  # 启动脚本
├── requirements.txt        # 依赖清单
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
3. **Analyzer** (分析节点): 提取关键发现，识别趋势和争议
4. **Generator** (生成节点): 生成结构化研究报告
5. **Quality** (质量节点): 质量检查，路由决策

## 质量控制

系统提供多维度质量控制：

- **内容完整性**: 报告长度和必要章节检查
- **来源覆盖**: 来源引用率检查
- **结构规范**: Markdown格式和章节层级检查
- **研究深度**: 发现数量和来源数量检查

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
