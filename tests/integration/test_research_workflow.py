"""研究工作流集成测试"""
import pytest
from app.core.graph import create_research_graph
from app.core.state import create_initial_state


@pytest.mark.asyncio
async def test_research_graph_creation():
    """测试研究工作流图创建"""
    graph = create_research_graph()
    assert graph is not None


@pytest.mark.asyncio
async def test_full_workflow_mock():
    """测试完整工作流（模拟）"""
    # 注意：这是一个框架测试，实际执行需要配置API密钥
    
    initial_state = create_initial_state(
        session_id="test-integration-001",
        topic="机器学习在金融科技中的应用",
        depth="quick"
    )
    
    # 验证初始状态
    assert initial_state["session_id"] == "test-integration-001"
    assert initial_state["topic"] == "机器学习在金融科技中的应用"
    assert initial_state["stage"] == "initialized"
