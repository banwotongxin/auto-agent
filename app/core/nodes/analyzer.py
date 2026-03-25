"""分析节点 - 分析综合收集的信息"""
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from app.core.state import ResearchState
from app.services.llm import get_llm
from app.services.vector_store import VectorStore


ANALYSIS_SYSTEM_PROMPT = """你是一个专业的研究分析专家。你的任务是分析收集到的资料，提取关键发现。

你需要：
1. 深入理解每个信息来源的核心观点
2. 识别不同来源之间的共识和分歧
3. 提取有证据支持的关键发现
4. 评估每个发现的可信度
5. 指出信息缺口和需要进一步验证的问题

分析原则：
- 基于证据，避免主观臆断
- 考虑多元观点，特别是对立观点
- 标注信息来源
- 评估可信度时要考虑来源质量和证据强度"""

ANALYSIS_USER_TEMPLATE = """请分析以下研究资料，提取关键发现。

研究主题: {topic}

收集到的资料（共{source_count}个来源）：

{sources_text}

请完成以下分析任务：

1. 提取5-10个关键发现，每个发现包含：
   - 主题/标题
   - 详细内容（基于资料的客观陈述）
   - 支持该发现的来源URL列表
   - 可信度评分（0-1之间）

2. 识别主要研究主题和趋势

3. 指出信息缺口和争议点

请以JSON格式返回：
{{
    "findings": [
        {{
            "topic": "发现主题",
            "content": "详细内容",
            "supporting_sources": ["url1", "url2"],
            "confidence": 0.85
        }}
    ],
    "key_themes": ["主题1", "主题2", "主题3"],
    "controversial_points": ["争议点1", "争议点2"],
    "information_gaps": ["缺口1", "缺口2"],
    "summary": "整体分析摘要（300字以内）"
}}

注意：只返回JSON，不要包含其他说明文字。"""


class AnalysisNodeExecutor:
    """分析节点执行器"""
    
    def __init__(self):
        self.vector_store = VectorStore()
        self.llm = get_llm()
    
    def _format_sources(self, sources: List[Dict]) -> str:
        """格式化来源文本"""
        formatted = []
        for i, source in enumerate(sources, 1):
            content = source.get("content", "")[:1500]  # 限制每个来源长度
            formatted.append(
                f"### 来源{i}\n"
                f"URL: {source.get('url', '')}\n"
                f"标题: {source.get('title', '')}\n"
                f"内容: {content}\n"
            )
        return "\n\n".join(formatted)
    
    async def execute(self, state: ResearchState) -> ResearchState:
        """分析节点主逻辑"""
        sources = state.get("sources", [])
        
        if not sources:
            state["error_messages"] = state.get("error_messages", []) + ["No sources to analyze"]
            state["stage"] = "failed"
            return state
        
        try:
            # 1. 将来源存入向量存储（用于后续检索）
            await self.vector_store.add_sources(
                state["session_id"],
                sources
            )
            
            # 2. 准备分析输入
            sources_text = self._format_sources(sources[:15])  # 限制分析的来源数量
            
            # 3. 构建提示
            prompt = ChatPromptTemplate.from_messages([
                ("system", ANALYSIS_SYSTEM_PROMPT),
                ("human", ANALYSIS_USER_TEMPLATE)
            ])
            
            # 4. 执行分析
            chain = prompt | self.llm
            
            response = await chain.ainvoke({
                "topic": state["topic"],
                "source_count": len(sources),
                "sources_text": sources_text
            })
            
            # 5. 解析结果
            try:
                parser = JsonOutputParser()
                analysis_result = parser.parse(response.content)
            except Exception:
                # 如果解析失败，手动提取
                analysis_result = self._extract_analysis_fallback(response.content)
            
            # 6. 更新状态
            state["findings"] = analysis_result.get("findings", [])
            state["analysis_summary"] = analysis_result.get("summary", "")
            state["stage"] = "generating"
            
            # 7. 更新成本追踪
            cost_tracker = state.get("cost_tracker", {})
            cost_tracker["llm_calls"] = cost_tracker.get("llm_calls", 0) + 1
            state["cost_tracker"] = cost_tracker
            
        except Exception as e:
            state["error_messages"] = state.get("error_messages", []) + [f"Analysis error: {str(e)}"]
            state["stage"] = "failed"
        
        return state
    
    def _extract_analysis_fallback(self, content: str) -> Dict:
        """解析失败的备用提取方法"""
        return {
            "findings": [{"topic": "分析结果", "content": content[:1000], "supporting_sources": [], "confidence": 0.5}],
            "key_themes": [],
            "controversial_points": [],
            "information_gaps": [],
            "summary": content[:500]
        }


async def analyzing_node(state: ResearchState) -> ResearchState:
    """分析节点入口函数"""
    executor = AnalysisNodeExecutor()
    return await executor.execute(state)
