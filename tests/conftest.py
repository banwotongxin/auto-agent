"""测试配置

pytest配置和测试fixtures定义。
"""
import pytest
from typing import Dict, Any, List
from app.core.state import create_initial_state


@pytest.fixture
def sample_research_state() -> Dict[str, Any]:
    """示例研究状态（快速模式）"""
    return create_initial_state(
        session_id="test-001",
        topic="人工智能在医疗诊断中的应用",
        depth="quick"
    )


@pytest.fixture
def sample_research_state_standard() -> Dict[str, Any]:
    """示例研究状态（标准模式）"""
    return create_initial_state(
        session_id="test-002",
        topic="机器学习在金融风控中的应用",
        depth="standard"
    )


@pytest.fixture
def sample_research_state_deep() -> Dict[str, Any]:
    """示例研究状态（深度模式）"""
    return create_initial_state(
        session_id="test-003",
        topic="区块链技术在供应链管理中的应用与挑战",
        depth="deep"
    )


@pytest.fixture
def sample_search_results() -> List[Dict[str, Any]]:
    """示例搜索结果"""
    return [
        {
            "url": "https://example.com/article1",
            "title": "AI in Healthcare",
            "content": "Artificial intelligence is transforming healthcare with improved diagnostic accuracy.",
            "relevance_score": 0.85,
            "credibility_score": 0.8,
            "source_type": "academic",
            "combined_score": 0.83,
            "key_points": ["AI improves diagnostic accuracy", "Machine learning in medical imaging"]
        },
        {
            "url": "https://example.com/article2",
            "title": "Medical AI Applications",
            "content": "Recent advances in medical AI show promising results in early disease detection.",
            "relevance_score": 0.75,
            "credibility_score": 0.7,
            "source_type": "news",
            "combined_score": 0.73,
            "key_points": ["Early disease detection", "AI-assisted diagnosis"]
        },
        {
            "url": "https://example.com/article3",
            "title": "Healthcare Technology Trends",
            "content": "Overview of healthcare technology trends including AI, IoT, and telemedicine.",
            "relevance_score": 0.65,
            "credibility_score": 0.6,
            "source_type": "blog",
            "combined_score": 0.63,
            "key_points": ["Technology trends", "Digital health"]
        }
    ]


@pytest.fixture
def sample_sources() -> List[Dict[str, Any]]:
    """示例筛选后来源"""
    return [
        {
            "url": "https://nature.com/articles/ai-diagnostics",
            "title": "AI in Medical Diagnostics",
            "content": "This Nature article discusses advances in AI for medical diagnostics...",
            "relevance_score": 0.9,
            "credibility_score": 0.95,
            "source_type": "academic",
            "combined_score": 0.92,
            "word_count": 3500,
            "key_points": [
                "Deep learning models achieve expert-level accuracy",
                "AI assists but does not replace human clinicians"
            ]
        },
        {
            "url": "https://who.int/health-topics/ai",
            "title": "WHO Guidelines on AI in Healthcare",
            "content": "The WHO provides guidelines on the ethical use of AI in healthcare...",
            "relevance_score": 0.88,
            "credibility_score": 0.9,
            "source_type": "official",
            "combined_score": 0.89,
            "word_count": 2800,
            "key_points": [
                "Ethical considerations for AI in healthcare",
                "WHO recommendations for AI deployment"
            ]
        }
    ]


@pytest.fixture
def sample_findings() -> List[Dict[str, Any]]:
    """示例研究发现"""
    return [
        {
            "topic": "AI提高诊断准确率",
            "content": "研究表明AI在某些疾病诊断中准确率达到95%以上，特别是皮肤癌和糖尿病视网膜病变的早期检测。",
            "supporting_sources": [
                "https://nature.com/articles/ai-diagnostics",
                "https://who.int/health-topics/ai"
            ],
            "confidence": 0.9,
            "evidence_strength": "strong"
        },
        {
            "topic": "AI辅助而非替代医生",
            "content": "WHO指南强调AI应作为辅助工具，帮助医生做出更好决策，而非替代人类判断。",
            "supporting_sources": ["https://who.int/health-topics/ai"],
            "confidence": 0.85,
            "evidence_strength": "strong"
        }
    ]


@pytest.fixture
def sample_analysis_summary() -> str:
    """示例分析摘要"""
    return """
    本研究分析了人工智能在医疗诊断领域的应用现状和发展趋势。

    主要发现：
    1. AI诊断系统在多个疾病领域展现出专家级准确率
    2. 监管机构和国际组织正在制定AI医疗设备的使用指南
    3. 数据隐私和安全是主要挑战

    研究表明，AI技术有望显著改善医疗诊断的效率和准确性，但仍需在监管、伦理和技术层面持续完善。
    """


@pytest.fixture
def sample_plan() -> Dict[str, Any]:
    """示例研究计划"""
    return {
        "topic": "人工智能在医疗诊断中的应用",
        "topic_analysis": "研究AI技术，特别是深度学习在医疗诊断中的最新进展和应用",
        "sub_questions": [
            "AI诊断系统的准确率有多高？",
            "哪些疾病领域应用最广泛？",
            "监管机构如何评估AI医疗设备？",
            "面临哪些伦理和安全挑战？"
        ],
        "search_queries": [
            "AI medical diagnosis accuracy 2024",
            "deep learning healthcare applications",
            "FDA AI medical device approval",
            "AI ethics in healthcare"
        ],
        "search_strategy": {
            "rounds": 2,
            "sources_per_round": 15,
            "focus_areas": ["技术进展", "监管政策", "伦理考量"],
            "quality_criteria": "优先学术和政府来源"
        },
        "expected_outputs": [
            "AI诊断准确率数据",
            "应用案例分析",
            "监管政策综述"
        ],
        "estimated_time_minutes": 20
    }
