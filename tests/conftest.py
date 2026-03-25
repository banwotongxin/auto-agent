"""测试配置"""
import pytest
from app.core.state import create_initial_state


@pytest.fixture
def sample_research_state():
    """示例研究状态"""
    return create_initial_state(
        session_id="test-001",
        topic="人工智能在医疗诊断中的应用",
        depth="quick"
    )


@pytest.fixture
def sample_search_results():
    """示例搜索结果"""
    return [
        {
            "url": "https://example.com/article1",
            "title": "AI in Healthcare",
            "content": "Artificial intelligence is transforming healthcare...",
            "relevance_score": 0.85,
            "credibility_score": 0.8
        },
        {
            "url": "https://example.com/article2",
            "title": "Medical AI Applications",
            "content": "Recent advances in medical AI...",
            "relevance_score": 0.75,
            "credibility_score": 0.7
        }
    ]


@pytest.fixture
def sample_findings():
    """示例研究发现"""
    return [
        {
            "topic": "AI提高诊断准确率",
            "content": "研究表明AI在某些疾病诊断中准确率达到95%以上",
            "supporting_sources": ["https://example.com/article1"],
            "confidence": 0.9
        }
    ]
