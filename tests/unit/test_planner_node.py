"""规划节点单元测试"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from app.core.nodes.planner import planning_node


@pytest.mark.asyncio
async def test_planning_node_success(sample_research_state):
    """测试规划节点成功执行"""
    
    # 模拟LLM响应
    mock_response = {
        "topic": "人工智能在医疗诊断中的应用",
        "sub_questions": ["AI如何提高诊断准确率？", "有哪些成功的应用案例？"],
        "search_queries": ["AI medical diagnosis accuracy", "healthcare AI applications 2024"],
        "search_strategy": {"rounds": 1, "sources_per_round": 10},
        "expected_outputs": ["诊断准确率数据", "应用案例分析"],
        "estimated_time_minutes": 15
    }
    
    with patch("app.core.nodes.planner.get_llm") as mock_get_llm:
        mock_llm = Mock()
        mock_llm.ainvoke = AsyncMock(return_value=Mock(
            content=str(mock_response).replace("'", '"')
        ))
        mock_get_llm.return_value = mock_llm
        
        # 执行节点
        result = await planning_node(sample_research_state)
        
        # 验证结果
        assert result["stage"] == "searching"
        assert "plan" in result


@pytest.mark.asyncio
async def test_planning_node_error(sample_research_state):
    """测试规划节点错误处理"""
    
    with patch("app.core.nodes.planner.get_llm") as mock_get_llm:
        mock_get_llm.side_effect = Exception("LLM Error")
        
        result = await planning_node(sample_research_state)
        
        assert result["stage"] == "failed"
        assert any("Planning error" in msg for msg in result["error_messages"])
