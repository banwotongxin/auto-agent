"""报告生成节点 - 生成结构化研究报告"""
from langchain_core.prompts import ChatPromptTemplate
from app.core.state import ResearchState
from app.services.llm import get_llm


REPORT_SYSTEM_PROMPT = """你是一个专业的研究报告撰写专家。你的任务是基于分析结果生成高质量的研究报告。

报告撰写原则：
1. 结构清晰，逻辑严密
2. 客观陈述，基于证据
3. 语言专业，表述准确
4. 适当引用来源
5. 考虑不同观点和潜在限制

报告格式要求：
- 使用Markdown格式
- 合理使用标题层级
- 重要观点后用括号标注引用来源
- 关键数据和事实需要标注出处"""

REPORT_USER_TEMPLATE = """请基于以下分析结果，生成一份专业的研究报告。

研究主题: {topic}

关键发现（共{finding_count}个）：

{findings_text}

分析摘要:
{analysis_summary}

参考来源数量: {source_count}

研究深度级别: {depth}

请生成一份结构化的Markdown格式研究报告，包含以下部分：

# {topic}

## 执行摘要
- 研究背景和目的（2-3句）
- 主要发现概述（3-5个要点）
- 核心结论和建议

## 研究背景
- 主题简介和重要性
- 研究范围和方法说明
- 资料来源概述

## 核心发现
针对每个关键发现进行深入分析：

### [发现1主题]
详细分析内容，包括：
- 发现的详细说明
- 支持证据
- 来源引用
- 可信度评估

### [发现2主题]
...

## 讨论与分析
- 主要趋势和模式识别
- 不同观点的对比
- 潜在影响和意义

## 限制与展望
- 本研究的局限性
- 信息缺口说明
- 未来研究方向建议

## 结论
- 核心结论总结
- 实际应用建议

## 参考来源
- 按可信度排序列出主要来源
- 格式：标题 - URL

要求：
- 报告总长度根据深度级别调整（quick: 1500字左右, standard: 3000字左右, deep: 5000字左右）
- 使用专业的学术写作风格
- 重要数据和观点后标注来源，如：(来源: https://...)
- 合理使用列表、表格等格式增强可读性"""


class GeneratorNodeExecutor:
    """报告生成节点执行器"""
    
    def __init__(self):
        self.llm = get_llm()
    
    def _format_findings(self, findings: List[Dict]) -> str:
        """格式化发现文本"""
        formatted = []
        for i, finding in enumerate(findings, 1):
            sources = finding.get("supporting_sources", [])
            formatted.append(
                f"### 发现{i}: {finding.get('topic', '')}\n"
                f"内容: {finding.get('content', '')}\n"
                f"支持来源: {', '.join(sources[:3])}\n"
                f"可信度: {finding.get('confidence', 0)}\n"
            )
        return "\n\n".join(formatted)
    
    async def execute(self, state: ResearchState) -> ResearchState:
        """报告生成节点主逻辑"""
        
        findings = state.get("findings", [])
        
        if not findings:
            state["error_messages"] = state.get("error_messages", []) + ["No findings to generate report"]
            state["stage"] = "failed"
            return state
        
        try:
            # 准备输入
            findings_text = self._format_findings(findings)
            
            # 构建提示
            prompt = ChatPromptTemplate.from_messages([
                ("system", REPORT_SYSTEM_PROMPT),
                ("human", REPORT_USER_TEMPLATE)
            ])
            
            # 执行生成
            chain = prompt | self.llm
            
            response = await chain.ainvoke({
                "topic": state["topic"],
                "finding_count": len(findings),
                "findings_text": findings_text,
                "analysis_summary": state.get("analysis_summary", ""),
                "source_count": len(state.get("sources", [])),
                "depth": state["depth"]
            })
            
            # 更新状态
            state["final_report"] = response.content
            state["stage"] = "quality_check"
            
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
