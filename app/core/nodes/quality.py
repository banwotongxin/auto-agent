"""质量控制节点 - 检查研究质量并做出路由决策

自动深度研究智能体的核心组件，负责：
1. 检查报告内容完整性和质量
2. 验证来源引用覆盖率
3. 评估研究深度
4. 做出路由决策（继续/完成/失败）
"""
from typing import Literal, List, Dict, Any, Tuple, Optional
from app.core.state import ResearchState


# 质量标准配置（降低标准，避免循环）
QUALITY_STANDARDS = {
    "quick": {
        "min_report_words": 1000,
        "min_sources": 3,
        "min_findings": 2,
        "min_source_coverage": 0.2,
        "required_sections": ["执行摘要", "核心发现", "结论"]
    },
    "standard": {
        "min_report_words": 2000,
        "min_sources": 5,  # 从 15 降低到 5
        "min_findings": 3,  # 从 5 降低到 3
        "min_source_coverage": 0.3,
        "required_sections": ["执行摘要", "核心发现", "结论"]
    },
    "deep": {
        "min_report_words": 4000,
        "min_sources": 10,  # 从 30 降低到 10
        "min_findings": 5,  # 从 8 降低到 5
        "min_source_coverage": 0.4,
        "required_sections": ["执行摘要", "研究背景", "核心发现", "讨论与分析", "结论"]
    }
}


class QualityMetrics:
    """质量指标计算器"""
    
    @staticmethod
    def count_words(text: str) -> int:
        """统计字数（中文+英文）"""
        if not text:
            return 0
        
        # 简单统计：中文按字符，英文按单词
        chinese_chars = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
        english_words = len([w for w in text.split() if w.isalpha()])
        
        return chinese_chars + english_words
    
    @staticmethod
    def count_markdown_headers(text: str) -> int:
        """统计Markdown标题数量"""
        if not text:
            return 0
        return len([line for line in text.split('\n') if line.strip().startswith('#')])

    @staticmethod
    def count_sections(text: str) -> int:
        """统计主要章节数量"""
        if not text:
            return 0
        return len([line for line in text.split('\n') if line.strip().startswith('## ')])
    
    @staticmethod
    def calculate_source_coverage(report: str, sources: List[Dict[str, Any]]) -> Tuple[int, float]:
        """
        计算来源覆盖率

        Returns:
            (被引用来源数, 覆盖率)
        """
        if not sources:
            return 0, 0.0

        report = report or ""  # 确保 report 不为 None
        cited_count = 0
        for source in sources:
            url = source.get("url", "")
            title = source.get("title", "")

            # 检查URL或标题是否在报告中被引用
            if url and (url in report or title[:30] in report):
                cited_count += 1

        coverage = cited_count / len(sources)
        return cited_count, coverage
    
    @staticmethod
    def assess_finding_quality(findings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        评估发现质量
        
        Returns:
            质量评估结果
        """
        if not findings:
            return {"avg_confidence": 0.0, "high_quality_count": 0, "total": 0}
        
        confidences = [f.get("confidence", 0.5) for f in findings]
        avg_confidence = sum(confidences) / len(confidences)
        high_quality_count = sum(1 for c in confidences if c >= 0.7)
        
        return {
            "avg_confidence": round(avg_confidence, 3),
            "high_quality_count": high_quality_count,
            "total": len(findings),
            "min_confidence": min(confidences),
            "max_confidence": max(confidences)
        }


class QualityChecker:
    """质量检查器"""
    
    def __init__(self, depth: str = "standard"):
        self.standards = QUALITY_STANDARDS.get(depth, QUALITY_STANDARDS["standard"])
        self.depth = depth
        self.metrics = QualityMetrics()
    
    def check_all(self, state: ResearchState) -> Dict[str, Any]:
        """
        执行全面质量检查
        
        Args:
            state: 研究状态
            
        Returns:
            质量检查结果
        """
        report = state.get("final_report", "")
        sources = state.get("sources", [])
        findings = state.get("findings", [])
        
        # 执行各项检查
        content_result = self._check_content(report)
        structure_result = self._check_structure(report)
        source_result = self._check_source_coverage(report, sources)
        depth_result = self._check_research_depth(findings, sources)
        finding_result = self._check_findings_quality(findings)
        
        # 汇总结果
        all_checks = {
            "content": content_result,
            "structure": structure_result,
            "source_coverage": source_result,
            "research_depth": depth_result,
            "findings_quality": finding_result
        }
        
        # 判断是否通过
        critical_checks = ["content", "source_coverage", "research_depth"]
        passed = all(all_checks[c]["passed"] for c in critical_checks)
        
        # 生成详细报告
        quality_report = {
            "passed": passed,
            "checks": all_checks,
            "overall_score": self._calculate_overall_score(all_checks),
            "recommendation": self._get_recommendation(all_checks, state),
            "improvement_suggestions": self._get_improvement_suggestions(all_checks)
        }
        
        return quality_report
    
    def _check_content(self, report: str) -> Dict[str, Any]:
        """检查内容完整性"""
        report = report or ""  # 确保 report 不为 None
        word_count = self.metrics.count_words(report)
        min_words = self.standards["min_report_words"]

        # 检查必要章节
        required_sections = self.standards["required_sections"]
        missing_sections = [s for s in required_sections if s not in report]
        
        # 评估内容充实度
        has_substantial_content = word_count >= min_words * 0.8  # 允许20%误差
        
        passed = len(missing_sections) == 0 and has_substantial_content
        
        return {
            "passed": passed,
            "word_count": word_count,
            "min_words": min_words,
            "missing_sections": missing_sections,
            "score": min(word_count / min_words, 1.0) if min_words > 0 else 1.0
        }
    
    def _check_structure(self, report: str) -> Dict[str, Any]:
        """检查报告结构"""
        report = report or ""  # 确保 report 不为 None
        header_count = self.metrics.count_markdown_headers(report)
        section_count = self.metrics.count_sections(report)

        # 评估结构完整性
        has_good_structure = header_count >= 5 and section_count >= 4

        # 检查是否有适当的层次
        has_hierarchy = report.count("# ") >= 2 and report.count("## ") >= 3

        passed = has_good_structure and has_hierarchy

        return {
            "passed": passed,
            "header_count": header_count,
            "section_count": section_count,
            "score": min(header_count / 10, 1.0) if header_count > 0 else 0.0
        }
    
    def _check_source_coverage(self, report: str, sources: List[Dict[str, Any]]) -> Dict[str, Any]:
        """检查来源引用情况"""
        cited_count, coverage = self.metrics.calculate_source_coverage(report, sources)
        min_coverage = self.standards["min_source_coverage"]
        
        passed = coverage >= min_coverage
        
        return {
            "passed": passed,
            "cited_count": cited_count,
            "total_sources": len(sources),
            "coverage": round(coverage, 3),
            "min_required": min_coverage,
            "score": coverage
        }
    
    def _check_research_depth(self, findings: List[Dict], sources: List[Dict]) -> Dict[str, Any]:
        """检查研究深度"""
        min_findings = self.standards["min_findings"]
        min_sources = self.standards["min_sources"]
        
        passed = len(findings) >= min_findings and len(sources) >= min_sources
        
        return {
            "passed": passed,
            "findings_count": len(findings),
            "min_findings_required": min_findings,
            "sources_count": len(sources),
            "min_sources_required": min_sources,
            "score": min(len(findings) / min_findings, 1.0) if min_findings > 0 else 0.0
        }
    
    def _check_findings_quality(self, findings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """检查发现质量"""
        quality = self.metrics.assess_finding_quality(findings)
        
        # 高质量发现占比
        if quality["total"] > 0:
            high_ratio = quality["high_quality_count"] / quality["total"]
        else:
            high_ratio = 0.0
        
        passed = quality["avg_confidence"] >= 0.5 and high_ratio >= 0.3
        
        return {
            "passed": passed,
            "avg_confidence": quality["avg_confidence"],
            "high_quality_count": quality["high_quality_count"],
            "total": quality["total"],
            "score": quality["avg_confidence"]
        }
    
    def _calculate_overall_score(self, checks: Dict[str, Dict]) -> float:
        """计算综合质量分数"""
        weights = {
            "content": 0.30,
            "structure": 0.15,
            "source_coverage": 0.25,
            "research_depth": 0.20,
            "findings_quality": 0.10
        }
        
        total_score = sum(
            checks[key]["score"] * weights[key]
            for key in weights
            if key in checks
        )
        
        return round(total_score, 3)
    
    def _get_recommendation(
        self, 
        checks: Dict[str, Any], 
        state: ResearchState
    ) -> Literal["completed", "needs_more_search", "needs_reanalysis", "failed"]:
        """基于检查结果给出建议"""
        
        # 所有关键检查都通过
        if all(checks[key]["passed"] for key in ["content", "source_coverage", "research_depth"]):
            return "completed"
        
        # 检查迭代次数
        iteration_count = state.get("iteration_count", 0)
        if iteration_count >= 2:
            # 超过最大迭代次数，检查是否达到最低标准
            if checks["content"]["passed"] and checks["research_depth"]["passed"]:
                return "completed"  # 达到最低标准，强制完成
            else:
                return "failed"  # 未达到最低标准
        
        # 来源覆盖不足 -> 需要更多搜索
        if not checks["source_coverage"]["passed"]:
            return "needs_more_search"
        
        # 内容不足 -> 需要重新分析/生成
        if not checks["content"]["passed"]:
            return "needs_reanalysis"
        
        # 深度不足 -> 需要更多搜索
        if not checks["research_depth"]["passed"]:
            return "needs_more_search"
        
        return "completed"
    
    def _get_improvement_suggestions(self, checks: Dict[str, Any]) -> List[str]:
        """生成改进建议"""
        suggestions = []
        
        if not checks["content"]["passed"]:
            missing = checks["content"].get("missing_sections", [])
            if missing:
                suggestions.append(f"补充缺失章节: {', '.join(missing)}")
            word_gap = checks["content"]["min_words"] - checks["content"]["word_count"]
            if word_gap > 0:
                suggestions.append(f"增加约{word_gap}字的内容")
        
        if not checks["source_coverage"]["passed"]:
            gap = checks["source_coverage"]["min_required"] - checks["source_coverage"]["coverage"]
            suggestions.append(f"来源覆盖率不足，需增加约{int(gap * 100)}%的引用")
        
        if not checks["research_depth"]["passed"]:
            findings_gap = checks["research_depth"]["min_findings_required"] - checks["research_depth"]["findings_count"]
            if findings_gap > 0:
                suggestions.append(f"发现数量不足，需补充{findings_gap}个关键发现")
        
        if not checks["structure"]["passed"]:
            suggestions.append("优化报告结构，增加章节层级")
        
        if not checks["findings_quality"]["passed"]:
            suggestions.append("部分发现可信度较低，建议补充高质量来源")
        
        return suggestions


class QualityController:
    """质量控制控制器（兼容性别名）"""
    
    def check_report_quality(self, state: ResearchState) -> Dict[str, Any]:
        """检查报告质量"""
        depth = state.get("depth", "standard")
        checker = QualityChecker(depth)
        return checker.check_all(state)


async def quality_check_node(state: ResearchState) -> ResearchState:
    """质量控制节点 - 只做一轮检查，直接完成"""
    
    depth = state.get("depth", "standard")
    checker = QualityChecker(depth)
    quality_result = checker.check_all(state)
    
    state["quality_report"] = quality_result
    state["quality_score"] = quality_result["overall_score"]
    state["quality_suggestions"] = quality_result.get("improvement_suggestions", [])
    state["stage"] = "completed"
    
    print(f"[QualityCheck] 质量检查完成 (score={quality_result['overall_score']:.2f})")
    return state


def route_decision(state: ResearchState) -> str:
    """路由决策 - 始终完成"""
    if state.get("stage") == "failed":
        return "failed"
    return "completed"
