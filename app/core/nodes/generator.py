"""报告生成节点 - 生成结构化研究报告

自动深度研究智能体的核心组件，负责：
1. 将分析结果转化为结构化报告
2. 生成专业的Markdown格式研究报告
3. 确保报告内容完整、逻辑清晰、引用准确
"""
from typing import List, Dict, Any
from langchain_core.prompts import ChatPromptTemplate
from app.core.state import ResearchState
from app.services.llm import get_llm


# 报告长度配置（字数）
REPORT_LENGTH_CONFIG = {
    "quick": {
        "min_words": 1500,
        "max_words": 2000,
        "findings_to_include": 5,
        "sources_to_cite": 10
    },
    "standard": {
        "min_words": 3000,
        "max_words": 4000,
        "findings_to_include": 8,
        "sources_to_cite": 20
    },
    "deep": {
        "min_words": 5000,
        "max_words": 7000,
        "findings_to_include": 12,
        "sources_to_cite": 30
    }
}


REPORT_SYSTEM_PROMPT = """你是一个专业的研究报告撰写专家，擅长将复杂的研究发现转化为清晰、专业的报告。

报告撰写核心原则：
1. **结构清晰**：使用逻辑递进的结构，引导读者理解研究全貌
2. **证据驱动**：所有观点基于可靠来源，避免无根据的推断
3. **客观中立**：呈现多元观点，包括争议和不确定性
4. **可读性强**：使用简洁专业的语言，适当使用格式增强可读性

报告质量标准：
- 执行摘要：简洁有力，3-5个核心要点
- 内容完整：覆盖主题的关键维度
- 引用准确：正确标注信息来源
- 深度适当：根据研究级别调整分析深度
- 格式规范：Markdown格式，层级清晰


引用规范：
- 直接引用：(来源: URL)
- 数据引用：(数据来源: URL)
- 观点引用：(观点来源: URL)
- 使用方括号标注，保持文本流畅"""


class SourceFormatter:
    """来源格式化工具"""
    
    @staticmethod
    def format_sources_for_report(
        sources: List[Dict[str, Any]], 
        max_cite: int = 20,
        sort_by: str = "credibility"
    ) -> str:
        """
        格式化来源列表
        
        Args:
            sources: 来源列表
            max_cite: 最大引用数
            sort_by: 排序方式 (credibility/relevance/combined)
            
        Returns:
            格式化的来源文本
        """
        if not sources:
            return ""
        
        # 排序
        sorted_sources = sorted(
            sources,
            key=lambda x: x.get(f"{sort_by}_score", 0.5),
            reverse=True
        )[:max_cite]
        
        formatted = []
        for i, source in enumerate(sorted_sources, 1):
            title = source.get("title", "Untitled")[:80]
            url = source.get("url", "")
            source_type = source.get("source_type", "web")
            credibility = source.get("credibility_score", 0.5)
            
            formatted.append(
                f"{i}. **{title}** ({source_type}, 可信度: {credibility:.0%})  \n   {url}"
            )
        
        return "\n".join(formatted)
    
    @staticmethod
    def create_citation_map(sources: List[Dict[str, Any]]) -> Dict[str, str]:
        """
        创建URL到短引用ID的映射
        
        Returns:
            {url: citation_key} 例如 {"https://...": "[来源1]"}
        """
        citation_map = {}
        for i, source in enumerate(sources, 1):
            url = source.get("url", "")
            if url:
                citation_map[url] = f"[来源{i}]"
        
        return citation_map


class ReportStructureBuilder:
    """报告结构构建器"""
    
    @staticmethod
    def build_report_outline(
        topic: str,
        findings: List[Dict[str, Any]],
        depth: str = "standard"
    ) -> Dict[str, Any]:
        """
        构建报告大纲
        
        Args:
            topic: 研究主题
            findings: 关键发现
            depth: 研究深度
            
        Returns:
            报告大纲
        """
        config = REPORT_LENGTH_CONFIG.get(depth, REPORT_LENGTH_CONFIG["standard"])
        
        outline = {
            "title": topic,
            "sections": [
                {"id": "executive_summary", "title": "执行摘要", "priority": 1},
                {"id": "background", "title": "研究背景", "priority": 2},
                {"id": "findings", "title": "核心发现", "priority": 3},
                {"id": "analysis", "title": "讨论与分析", "priority": 4},
                {"id": "limitations", "title": "局限与展望", "priority": 5},
                {"id": "conclusion", "title": "结论", "priority": 6},
                {"id": "references", "title": "参考来源", "priority": 7}
            ],
            "metadata": {
                "expected_length": config["min_words"],
                "findings_count": min(len(findings), config["findings_to_include"])
            }
        }
        
        return outline
    
    @staticmethod
    def format_findings_for_prompt(
        findings: List[Dict[str, Any]],
        sources: List[Dict[str, Any]],
        max_findings: int = 8
    ) -> str:
        """
        格式化发现用于报告生成提示
        
        Args:
            findings: 发现列表
            sources: 来源列表
            max_findings: 最大发现数
            
        Returns:
            格式化文本
        """
        # 按可信度排序
        sorted_findings = sorted(
            findings,
            key=lambda x: x.get("confidence", 0.5),
            reverse=True
        )[:max_findings]
        
        # 创建引用映射
        citation_map = SourceFormatter.create_citation_map(sources)
        
        formatted = []
        for i, finding in enumerate(sorted_findings, 1):
            topic = finding.get("topic", "")
            content = finding.get("content", "")
            confidence = finding.get("confidence", 0.5)
            evidence = finding.get("evidence_strength", "moderate")
            
            # 转换来源URL为引用
            supporting_sources = finding.get("supporting_sources", [])
            citations = []
            for url in supporting_sources[:3]:
                if url in citation_map:
                    citations.append(citation_map[url])
            
            citation_text = " ".join(citations) if citations else ""
            
            formatted.append(
                f"### 发现{i}: {topic}\n"
                f"**可信度**: {confidence:.0%} ({evidence})\n"
                f"**内容**: {content}\n"
                f"**来源**: {citation_text}\n"
            )
        
        return "\n\n".join(formatted)


class GeneratorNodeExecutor:
    """报告生成节点执行器"""
    
    def __init__(self):
        self.llm = get_llm()
        self.source_formatter = SourceFormatter()
        self.structure_builder = ReportStructureBuilder()
    
    def _prepare_report_context(self, state: ResearchState) -> Dict[str, Any]:
        """准备报告生成的上下文"""
        findings = state.get("findings", [])
        sources = state.get("sources", [])
        depth = state.get("depth", "standard")
        config = REPORT_LENGTH_CONFIG.get(depth, REPORT_LENGTH_CONFIG["standard"])
        
        # 格式化发现
        findings_text = self.structure_builder.format_findings_for_prompt(
            findings, sources, config["findings_to_include"]
        )
        
        # 格式化来源
        sources_text = self.source_formatter.format_sources_for_report(
            sources, config["sources_to_cite"]
        )
        
        # 获取分析摘要和其他分析结果
        analysis_summary = state.get("analysis_summary", "")
        key_themes = state.get("key_themes", [])
        controversial_points = state.get("controversial_points", [])
        information_gaps = state.get("information_gaps", [])
        
        # 构建分析讨论部分
        discussion_text = ""
        if key_themes:
            discussion_text += "**主要研究主题和趋势**: " + ", ".join(key_themes) + "\n\n"
        if controversial_points:
            discussion_text += "**争议点和不同观点**: " + "; ".join(controversial_points) + "\n\n"
        if information_gaps:
            discussion_text += "**信息缺口**: " + "; ".join(information_gaps) + "\n\n"
        
        return {
            "findings_text": findings_text,
            "sources_text": sources_text,
            "analysis_summary": analysis_summary,
            "discussion_text": discussion_text,
            "config": config
        }
    
    def _build_user_template(self, depth: str) -> str:
        """根据深度构建用户模板"""
        base_length = REPORT_LENGTH_CONFIG.get(depth, REPORT_LENGTH_CONFIG["standard"])["min_words"]
        
        return f"""请基于以下研究分析结果，生成一份专业的研究报告。

# 研究主题
{{topic}}

# 研究深度级别
{depth}（目标字数: {base_length}+ 字）

# 关键发现
{{findings_text}}

# 分析摘要
{{analysis_summary}}

# 讨论要点
{{discussion_text}}

# 参考来源
{{sources_text}}

请生成一份完整的Markdown格式研究报告，结构如下：

# {{topic}}

## 执行摘要
请用3-5个要点总结研究的核心发现、方法和结论。每个要点1-2句话。

## 研究背景
- 主题简介和重要性（为什么这个研究重要）
- 研究范围和方法说明
- 资料来源概述（来源数量、类型分布、可信度概况）

## 核心发现
针对主要发现进行详细分析：
- 每个发现用一个小节
- 说明发现的具体内容和意义
- 标注来源引用
- 评估可信度

## 讨论与分析
- 主要趋势和模式识别
- 不同观点和争议分析
- 研究的实际意义和应用价值

## 研究局限与未来方向
- 本研究的主要局限性
- 现有信息缺口
- 未来研究建议

## 结论
用简洁的语言总结核心结论和建议。

## 参考来源
按可信度排序的主要参考来源列表。

写作要求：
- 使用专业的学术写作风格
- 报告总字数 {base_length}-{base_length+1000} 字
- 重要数据和分析后标注来源
- 合理使用Markdown格式增强可读性
- 保持逻辑清晰、论述连贯"""
    
    async def execute(self, state: ResearchState) -> ResearchState:
        """报告生成节点主逻辑"""
        
        findings = state.get("findings", [])
        
        if not findings:
            state["error_messages"] = state.get("error_messages", []) + ["No findings to generate report"]
            state["stage"] = "failed"
            return state
        
        try:
            print(f"[Generator] 开始生成研究报告...")
            depth = state.get("depth", "standard")
            config = REPORT_LENGTH_CONFIG.get(depth, REPORT_LENGTH_CONFIG["standard"])
            print(f"[Generator] 研究深度: {depth}, 目标字数: {config['min_words']}-{config['max_words']}")
            
            # 准备上下文
            print("[Generator] 准备报告上下文...")
            context = self._prepare_report_context(state)
            
            # 构建提示
            prompt = ChatPromptTemplate.from_messages([
                ("system", REPORT_SYSTEM_PROMPT),
                ("human", self._build_user_template(depth))
            ])
            
            # 执行生成
            print(f"[Generator] 调用 LLM 生成报告 (max_tokens={config['min_words'] * 2})...")
            llm = get_llm(max_tokens=config["min_words"] * 2)
            chain = prompt | llm
            
            response = await chain.ainvoke({
                "topic": state["topic"],
                "depth": depth,
                "findings_text": context["findings_text"],
                "analysis_summary": context["analysis_summary"],
                "discussion_text": context["discussion_text"],
                "sources_text": context["sources_text"]
            })
            print(f"[Generator] 报告生成完成，长度: {len(response.content)} 字符")
            
            # 更新状态
            state["final_report"] = response.content
            state["report_outline"] = self.structure_builder.build_report_outline(
                state["topic"], findings, depth
            )
            state["stage"] = "quality_check"
            
            print("[Generator] 报告已生成，进入质量检查阶段...")
            
            # 更新成本追踪
            cost_tracker = state.get("cost_tracker", {})
            cost_tracker["llm_calls"] = cost_tracker.get("llm_calls", 0) + 1
            state["cost_tracker"] = cost_tracker
            
        except Exception as e:
            state["error_messages"] = state.get("error_messages", []) + [f"Generation error: {str(e)}"]
            state["stage"] = "failed"
        
        return state


async def generating_node(state: ResearchState) -> ResearchState:
    """报告生成节点入口函数"""
    executor = GeneratorNodeExecutor()
    return await executor.execute(state)
