"""质量控制节点 - 检查研究质量并做出路由决策"""
from typing import Literal, List, Dict, Any
from app.core.state import ResearchState


class QualityController:
    """质量控制控制器"""
    
    def check_report_quality(self, state: ResearchState) -> Dict[str, Any]:
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
        
        # 检查报告长度
        min_lengths = {"quick": 1000, "standard": 2000, "deep": 3500}
        min_length = min_lengths.get(state["depth"], 2000)
        
        # 检查必要章节
        required_sections = ["执行摘要", "研究背景", "结论"]
        has_sections = all(section in report for section in required_sections)
        
        return len(report) >= min_length and has_sections
    
    def _check_source_coverage(self, state: ResearchState) -> bool:
        """检查来源引用情况"""
        report = state.get("final_report", "")
        sources = state.get("sources", [])
        
        if not sources:
            return False
        
        # 检查是否有足够来源被引用（至少30%）
        cited_count = 0
        for source in sources:
            if source.get("url", "") in report:
                cited_count += 1
        
        coverage = cited_count / len(sources)
        return coverage >= 0.3
    
    def _check_structure(self, state: ResearchState) -> bool:
        """检查报告结构"""
        report = state.get("final_report", "")
        
        # 检查Markdown格式
        has_headers = report.count("#") >= 3
        has_paragraphs = len(report.split("\n\n")) >= 5
        
        return has_headers and has_paragraphs
    
    def _check_depth(self, state: ResearchState) -> bool:
        """检查研究深度"""
        findings = state.get("findings", [])
        sources = state.get("sources", [])
        
        min_findings = {"quick": 3, "standard": 5, "deep": 8}
        min_sources = {"quick": 5, "standard": 10, "deep": 20}
        
        return (
            len(findings) >= min_findings.get(state["depth"], 5) and
            len(sources) >= min_sources.get(state["depth"], 10)
        )
    
    def _get_recommendation(
        self,
        checks: Dict[str, bool],
        state: ResearchState
    ) -> Literal["completed", "needs_more_search", "needs_reanalysis"]:
        """基于检查结果给出建议"""
        
        if all(checks.values()):
            return "completed"
        
        # 检查迭代次数
        if state.get("iteration_count", 0) >= 2:
            # 超过最大迭代次数，强制完成
            return "completed"
        
        # 来源覆盖不足 -> 需要更多搜索
        if not checks.get("source_coverage", True):
            return "needs_more_search"
        
        # 结构或深度不足 -> 需要重新分析
        if not checks.get("structure_ok", True) or not checks.get("sufficient_depth", True):
            return "needs_reanalysis"
        
        return "completed"


async def quality_check_node(state: ResearchState) -> ResearchState:
    """质量控制节点"""
    
    controller = QualityController()
    quality_result = controller.check_report_quality(state)
    
    if quality_result["passed"]:
        state["stage"] = "completed"
    else:
        # 增加迭代计数
        state["iteration_count"] = state.get("iteration_count", 0) + 1
    
    return state


def route_decision(state: ResearchState) -> str:
    """
    路由决策函数
    
    返回:
        - needs_more_search: 需要更多搜索
        - needs_reanalysis: 需要重新分析
        - completed: 完成
        - failed: 失败
    """
    
    # 检查是否失败
    if state.get("stage") == "failed":
        return "failed"
    
    # 检查是否已完成
    if state.get("stage") == "completed":
        return "completed"
    
    # 检查迭代次数限制
    if state.get("iteration_count", 0) >= 2:
        return "completed"
    
    # 质量控制检查
    controller = QualityController()
    quality_result = controller.check_report_quality(state)
    
    if quality_result["passed"]:
        return "completed"
    
    return quality_result["recommendation"]
