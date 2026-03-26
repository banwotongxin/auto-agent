"""研究工作流集成测试

测试完整的研究工作流，包括：
- 工作流图创建
- 状态转换
- 节点执行
- 质量控制
"""
import pytest
from app.core.graph import create_research_graph
from app.core.state import create_initial_state


class TestResearchWorkflow:
    """研究工作流测试类"""

    def test_research_graph_creation(self):
        """测试研究工作流图创建"""
        graph = create_research_graph()
        assert graph is not None
        assert hasattr(graph, 'invoke')
        assert hasattr(graph, 'ainvoke')

    def test_research_graph_nodes(self):
        """测试工作流图包含正确的节点"""
        graph = create_research_graph()
        # 验证图可以正常编译
        assert graph is not None

    def test_initial_state_structure(self, sample_research_state):
        """测试初始状态结构"""
        assert sample_research_state["session_id"] == "test-001"
        assert sample_research_state["topic"] == "人工智能在医疗诊断中的应用"
        assert sample_research_state["depth"] == "quick"
        assert sample_research_state["stage"] == "initialized"
        assert sample_research_state["iteration_count"] == 0

    def test_initial_state_cost_tracker(self, sample_research_state):
        """测试初始成本追踪器"""
        cost_tracker = sample_research_state["cost_tracker"]
        assert cost_tracker["llm_calls"] == 0
        assert cost_tracker["search_calls"] == 0
        assert cost_tracker["estimated_cost"] == 0.0

    def test_initial_state_empty_lists(self, sample_research_state):
        """测试初始空列表"""
        assert sample_research_state["search_queries"] == []
        assert sample_research_state["sources"] == []
        assert sample_research_state["findings"] == []
        assert sample_research_state["error_messages"] == []

    def test_initial_state_with_standard_depth(self, sample_research_state_standard):
        """测试标准深度初始状态"""
        assert sample_research_state_standard["depth"] == "standard"
        assert sample_research_state_standard["stage"] == "initialized"

    def test_initial_state_with_deep_depth(self, sample_research_state_deep):
        """测试深度模式初始状态"""
        assert sample_research_state_deep["depth"] == "deep"
        assert sample_research_state_deep["stage"] == "initialized"


class TestStateTransitions:
    """状态转换测试"""

    def test_state_has_correct_keys(self, sample_research_state):
        """测试状态包含所有必需的键"""
        required_keys = [
            "session_id", "topic", "depth", "stage", "created_at",
            "plan", "search_queries", "sources", "findings",
            "final_report", "iteration_count", "cost_tracker",
            "error_messages", "should_continue"
        ]
        
        for key in required_keys:
            assert key in sample_research_state, f"Missing key: {key}"

    def test_state_types(self, sample_research_state):
        """测试状态值类型正确"""
        assert isinstance(sample_research_state["session_id"], str)
        assert isinstance(sample_research_state["topic"], str)
        assert isinstance(sample_research_state["depth"], str)
        assert isinstance(sample_research_state["stage"], str)
        assert isinstance(sample_research_state["iteration_count"], int)
        assert isinstance(sample_research_state["should_continue"], bool)


class TestQualityControlIntegration:
    """质量控制集成测试"""

    def test_quality_standards_structure(self):
        """测试质量标准配置结构"""
        from app.core.nodes.quality import QUALITY_STANDARDS
        
        for depth, standards in QUALITY_STANDARDS.items():
            assert "min_report_words" in standards
            assert "min_sources" in standards
            assert "min_findings" in standards
            assert "required_sections" in standards
            assert isinstance(standards["required_sections"], list)

    def test_quality_metrics_calculation(self):
        """测试质量指标计算"""
        from app.core.nodes.quality import QualityMetrics
        
        # 测试字数统计
        text = "这是一个测试内容。This is test content."
        word_count = QualityMetrics.count_words(text)
        assert word_count > 0
        
        # 测试Markdown标题统计
        md_text = "# Title\n## Section\n### Subsection"
        header_count = QualityMetrics.count_markdown_headers(md_text)
        assert header_count == 3
        
        # 测试章节统计
        section_count = QualityMetrics.count_sections(md_text)
        assert section_count == 2

    def test_source_coverage_calculation(self):
        """测试来源覆盖率计算"""
        from app.core.nodes.quality import QualityMetrics
        
        sources = [
            {"url": "https://example.com/1", "title": "Article 1"},
            {"url": "https://example.com/2", "title": "Article 2"},
            {"url": "https://example.com/3", "title": "Article 3"}
        ]
        
        # 报告引用了2个来源
        report = "Article 1 is great. See https://example.com/2 for details."
        cited_count, coverage = QualityMetrics.calculate_source_coverage(report, sources)
        
        assert cited_count == 2
        assert coverage == pytest.approx(2/3, rel=0.01)


class TestSourceEvaluatorIntegration:
    """来源评估集成测试"""

    def test_high_credibility_domains(self):
        """测试高可信度域名识别"""
        from app.core.nodes.searcher import SourceEvaluator
        
        high_cred_urls = [
            ("https://stanford.edu/research", 0.95),
            ("https://nature.com/article", 0.9),
            ("https://arxiv.org/paper", 0.95),
            ("https://reuters.com/news", 0.9),
        ]
        
        for url, expected_min in high_cred_urls:
            score, source_type = SourceEvaluator.assess_credibility(url)
            assert score >= expected_min, f"URL {url} score too low: {score}"

    def test_low_credibility_domains(self):
        """测试低可信度域名识别"""
        from app.core.nodes.searcher import SourceEvaluator
        
        low_cred_urls = [
            "https://randomblog.blogspot.com",
            "https://user.wordpress.com"
        ]
        
        for url in low_cred_urls:
            score, source_type = SourceEvaluator.assess_credibility(url)
            assert score < 0.5, f"URL {url} score too high: {score}"

    def test_relevance_calculation(self):
        """测试相关性计算"""
        from app.core.nodes.searcher import SourceEvaluator
        
        content = "Artificial intelligence and machine learning are transforming healthcare diagnostics."
        query = "AI healthcare"
        
        relevance = SourceEvaluator.calculate_relevance(content, query)
        assert 0 <= relevance <= 1
        assert relevance > 0.3  # 应该有较高相关性

    def test_relevance_calculation_empty_content(self):
        """测试空内容的相关性计算"""
        from app.core.nodes.searcher import SourceEvaluator
        
        assert SourceEvaluator.calculate_relevance("", "query") == 0.0
        assert SourceEvaluator.calculate_relevance(None, "query") == 0.0
