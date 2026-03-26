"""分析节点 - 分析综合收集的信息

自动深度研究智能体的核心组件，负责：
1. 深入理解每个信息来源的核心观点
2. 识别不同来源之间的共识和分歧
3. 提取有证据支持的关键发现
4. 评估每个发现的可信度
5. 指出信息缺口和需要进一步验证的问题
"""
from typing import List, Dict, Any, Tuple
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from app.core.state import ResearchState
from app.services.llm import get_llm
from app.services.vector_store import VectorStore


ANALYSIS_SYSTEM_PROMPT = """你是一个专业的研究分析专家，擅长从大量资料中提取有价值的洞察。

你的核心任务：
1. 深入理解每个信息来源的核心观点和关键数据
2. 识别不同来源之间的共识、分歧和互补
3. 提取有强证据支持的关键发现
4. 评估每个发现的可信度（考虑来源质量、证据强度）
5. 指出信息缺口、研究局限性和需要进一步验证的问题

分析原则：
- 基于证据：只陈述有来源支持的事实
- 客观中立：呈现多元观点，包括对立观点
- 逻辑清晰：区分事实、推论和观点
- 可追溯：每个发现都标注支持来源

发现质量标准：
- 高可信度(0.8-1.0): 有多个高质量来源支持，数据充分
- 中可信度(0.5-0.8): 有来源支持，但可能存在争议或数据有限
- 低可信度(0.3-0.5): 来源有限或质量较低，需要进一步验证"""


class SourceAnalyzer:
    """来源分析器"""
    
    @staticmethod
    def aggregate_source_stats(sources: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        聚合来源统计信息
        
        Args:
            sources: 来源列表
            
        Returns:
            统计信息
        """
        if not sources:
            return {}
        
        # 按类型统计
        type_stats: Dict[str, int] = {}
        total_credibility = 0.0
        total_relevance = 0.0
        
        for source in sources:
            source_type = source.get("source_type", "unknown")
            type_stats[source_type] = type_stats.get(source_type, 0) + 1
            total_credibility += source.get("credibility_score", 0.5)
            total_relevance += source.get("relevance_score", 0.5)
        
        count = len(sources)
        
        return {
            "total_sources": count,
            "source_types": type_stats,
            "avg_credibility": round(total_credibility / count, 3),
            "avg_relevance": round(total_relevance / count, 3),
            "high_quality_count": sum(1 for s in sources if s.get("credibility_score", 0) >= 0.8)
        }
    
    @staticmethod
    def extract_consensus_and_divergence(sources: List[Dict[str, Any]]) -> Tuple[List[str], List[str]]:
        """
        识别来源间的共识和分歧
        
        Args:
            sources: 来源列表
            
        Returns:
            (共识列表, 分歧列表)
        """
        consensus = []
        divergence = []
        
        # 简单的关键词提取方法
        all_key_points: Dict[str, int] = {}
        
        for source in sources:
            key_points = source.get("key_points", [])
            for point in key_points:
                # 简化处理
                words = point.lower().split()[:5]
                key = " ".join(words)
                all_key_points[key] = all_key_points.get(key, 0) + 1
        
        # 出现多次的可能是共识
        for point, count in all_key_points.items():
            if count >= 2:
                consensus.append(f"{point}... (出现在{count}个来源)")
            elif count == 1:
                divergence.append(point)
        
        return consensus[:5], divergence[:5]


class FindingEvaluator:
    """发现评估器"""
    
    @staticmethod
    def evaluate_confidence(
        finding: Dict[str, Any],
        sources: List[Dict[str, Any]]
    ) -> float:
        """
        评估发现的可信度
        
        Args:
            finding: 发现
            sources: 所有来源
            
        Returns:
            可信度分数
        """
        supporting_urls = finding.get("supporting_sources", [])
        
        if not supporting_urls:
            return 0.3
        
        # 查找支持来源的质量
        source_qualities = []
        for url in supporting_urls:
            for source in sources:
                if source.get("url") == url:
                    source_qualities.append(source.get("credibility_score", 0.5))
                    break
        
        if not source_qualities:
            return 0.3
        
        # 可信度 = 来源平均质量 * 证据数量因子
        avg_quality = sum(source_qualities) / len(source_qualities)
        quantity_factor = min(len(source_qualities) / 3, 1.0)  # 最多3个来源
        
        return round(avg_quality * (0.7 + 0.3 * quantity_factor), 2)
    
    @staticmethod
    def enrich_finding(
        finding: Dict[str, Any],
        sources: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        丰富发现内容
        
        Args:
            finding: 发现
            sources: 所有来源
            
        Returns:
            丰富后的发现
        """
        # 评估可信度
        confidence = FindingEvaluator.evaluate_confidence(finding, sources)
        
        # 添加更多信息
        enriched = finding.copy()
        enriched["confidence"] = confidence
        enriched["evidence_strength"] = "strong" if confidence >= 0.8 else "moderate" if confidence >= 0.5 else "weak"
        
        return enriched


class AnalysisNodeExecutor:
    """分析节点执行器"""
    
    def __init__(self):
        self.vector_store = VectorStore()
        self.source_analyzer = SourceAnalyzer()
        self.finding_evaluator = FindingEvaluator()
    
    def _format_sources(self, sources: List[Dict]) -> str:
        """格式化来源文本用于分析"""
        formatted = []
        for i, source in enumerate(sources, 1):
            title = source.get("title", "")[:200]
            content = source.get("content", "")[:2000]  # 限制每个来源长度
            source_type = source.get("source_type", "web")
            credibility = source.get("credibility_score", 0.5)
            key_points = source.get("key_points", [])[:3]
            
            formatted.append(
                f"### 来源{i} [{source_type}] (可信度: {credibility:.2f})\n"
                f"**标题**: {title}\n"
                f"**URL**: {source.get('url', '')}\n"
                f"**关键点**: {'; '.join(key_points) if key_points else '无'}\n"
                f"**内容摘要**: {content}\n"
            )
        return "\n\n".join(formatted)
    
    def _format_findings_for_prompt(
        self, 
        findings: List[Dict], 
        sources: List[Dict]
    ) -> str:
        """格式化发现用于后续处理"""
        formatted = []
        for i, finding in enumerate(findings, 1):
            topic = finding.get("topic", "")
            content = finding.get("content", "")
            sources_urls = finding.get("supporting_sources", [])
            confidence = finding.get("confidence", 0.5)
            
            # 获取来源标题
            source_titles = []
            for url in sources_urls[:3]:
                for source in sources:
                    if source.get("url") == url:
                        source_titles.append(f"{source.get('title', '')[:50]}...")
                        break
            
            formatted.append(
                f"### 发现{i} (可信度: {confidence:.2f})\n"
                f"**主题**: {topic}\n"
                f"**内容**: {content}\n"
                f"**来源**: {', '.join(source_titles) if source_titles else '未标注'}\n"
            )
        return "\n\n".join(formatted)
    
    async def execute(self, state: ResearchState) -> ResearchState:
        """分析节点主逻辑"""
        sources = state.get("sources", [])
        depth = state.get("depth", "standard")
        
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
            
            # 2. 聚合来源统计
            source_stats = self.source_analyzer.aggregate_source_stats(sources)
            
            # 3. 准备分析输入
            sources_text = self._format_sources(sources[:20])  # 限制分析的来源数量
            
            # 4. 根据深度调整分析详细程度
            if depth == "deep":
                max_findings = 12
            elif depth == "standard":
                max_findings = 8
            else:
                max_findings = 5
            
            # 5. 构建提示
            prompt = ChatPromptTemplate.from_messages([
                ("system", ANALYSIS_SYSTEM_PROMPT),
                ("human", ANALYSIS_USER_TEMPLATE.format(
                    topic=state["topic"],
                    source_count=len(sources),
                    sources_text=sources_text,
                    max_findings=max_findings
                ))
            ])
            
            # 6. 执行分析
            llm = get_llm(max_tokens=4000 if depth == "deep" else 3000)
            chain = prompt | llm
            
            response = await chain.ainvoke({
                "topic": state["topic"],
                "source_count": len(sources),
                "sources_text": sources_text
            })
            
            # 7. 解析结果
            try:
                parser = JsonOutputParser()
                analysis_result = parser.parse(response.content)
            except Exception:
                # 如果解析失败，尝试备用提取
                analysis_result = self._extract_analysis_fallback(response.content)
            
            # 8. 丰富发现内容
            findings = analysis_result.get("findings", [])
            enriched_findings = [
                self.finding_evaluator.enrich_finding(f, sources)
                for f in findings
            ]
            
            # 9. 识别共识和分歧
            consensus, divergence = self.source_analyzer.extract_source_consensus(sources)
            
            # 10. 更新状态
            state["findings"] = enriched_findings
            state["analysis_summary"] = analysis_result.get("summary", "")
            state["source_stats"] = source_stats
            state["consensus"] = consensus
            state["divergence"] = divergence
            state["key_themes"] = analysis_result.get("key_themes", [])
            state["information_gaps"] = analysis_result.get("information_gaps", [])
            state["controversial_points"] = analysis_result.get("controversial_points", [])
            state["stage"] = "generating"
            
            # 11. 更新成本追踪
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
            "findings": [
                {
                    "topic": "分析结果",
                    "content": content[:2000],
                    "supporting_sources": [],
                    "confidence": 0.5
                }
            ],
            "key_themes": [],
            "controversial_points": [],
            "information_gaps": ["未能成功解析LLM输出"],
            "summary": content[:500]
        }


ANALYSIS_USER_TEMPLATE = """请分析以下研究资料，提取关键发现。

研究主题: {topic}

来源统计信息:
- 总来源数: {source_count}
- 来源列表如下:

{sources_text}

请完成以下分析任务（共提取{ max_findings}个关键发现）：

1. **提取关键发现**，每个发现必须包含：
   - topic: 发现主题/标题（简洁明确）
   - content: 详细内容（基于资料的客观陈述，100-200字）
   - supporting_sources: 支持该发现的来源URL列表（最多5个）
   - confidence: 可信度评分（0-1之间，基于来源质量）

2. **识别主要研究主题** (key_themes):
   - 列出3-5个核心主题/趋势

3. **指出信息缺口** (information_gaps):
   - 列出研究中缺乏信息的领域

4. **争议点** (controversial_points):
   - 列出存在不同观点或结论的领域

5. **整体分析摘要** (summary):
   - 300字以内的综合分析

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
    "summary": "整体分析摘要"
}}

注意：只返回JSON，不要包含其他说明文字。"""


async def analyzing_node(state: ResearchState) -> ResearchState:
    """分析节点入口函数"""
    executor = AnalysisNodeExecutor()
    return await executor.execute(state)
