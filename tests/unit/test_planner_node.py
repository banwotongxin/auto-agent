"""规划节点单元测试"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from app.core.nodes.planner import planning_node, _extract_search_queries, _get_depth_config


class TestPlannerNode:
    """规划节点测试类"""

    @pytest.mark.asyncio
    async def test_planning_node_success(self, sample_research_state):
        """测试规划节点成功执行"""
        mock_response = {
            "topic": "人工智能在医疗诊断中的应用",
            "topic_analysis": "研究AI在医疗诊断中的应用",
            "sub_questions": ["AI如何提高诊断准确率？", "有哪些成功的应用案例？"],
            "search_queries": [
                {"query": "AI medical diagnosis accuracy", "purpose": "获取准确率数据"},
                {"query": "healthcare AI applications 2024", "purpose": "了解最新应用"}
            ],
            "search_strategy": {"rounds": 1, "sources_per_round": 10},
            "expected_outputs": ["诊断准确率数据", "应用案例分析"],
            "estimated_time_minutes": 15
        }

        with patch("app.core.nodes.planner.get_llm") as mock_get_llm:
            mock_llm = Mock()
            mock_chain = Mock()
            mock_chain.ainvoke = AsyncMock(return_value=mock_response)
            mock_llm.return_value = mock_chain
            mock_get_llm.return_value = mock_chain

            # 执行节点
            result = await planning_node(sample_research_state)

            # 验证结果
            assert result["stage"] == "searching"
            assert "plan" in result
            assert len(result["search_queries"]) > 0

    @pytest.mark.asyncio
    async def test_planning_node_with_standard_depth(self, sample_research_state_standard):
        """测试规划节点标准深度模式"""
        mock_response = {
            "topic": "机器学习在金融风控中的应用",
            "sub_questions": ["ML如何改进风控模型？", "有哪些应用案例？"],
            "search_queries": ["machine learning credit risk", "fintech ML applications"],
            "search_strategy": {"rounds": 2, "sources_per_round": 15},
            "expected_outputs": ["风控模型改进方案"],
            "estimated_time_minutes": 20
        }

        with patch("app.core.nodes.planner.get_llm") as mock_get_llm:
            mock_llm = Mock()
            mock_chain = Mock()
            mock_chain.ainvoke = AsyncMock(return_value=mock_response)
            mock_llm.return_value = mock_chain
            mock_get_llm.return_value = mock_chain

            result = await planning_node(sample_research_state_standard)

            assert result["stage"] == "searching"
            assert result["depth"] == "standard"

    @pytest.mark.asyncio
    async def test_planning_node_error_handling(self, sample_research_state):
        """测试规划节点错误处理"""
        with patch("app.core.nodes.planner.get_llm") as mock_get_llm:
            mock_get_llm.side_effect = Exception("LLM Error")

            result = await planning_node(sample_research_state)

            assert result["stage"] == "failed"
            assert len(result["error_messages"]) > 0
            assert any("Planning error" in msg for msg in result["error_messages"])


class TestPlannerHelperFunctions:
    """规划节点辅助函数测试"""

    def test_get_depth_config_quick(self):
        """测试快速模式配置"""
        config = _get_depth_config("quick")
        assert config["rounds"] == 1
        assert config["min_sources"] == 5
        assert config["max_sources"] == 10

    def test_get_depth_config_standard(self):
        """测试标准模式配置"""
        config = _get_depth_config("standard")
        assert config["rounds"] == 2
        assert config["min_sources"] == 15
        assert config["max_sources"] == 20

    def test_get_depth_config_deep(self):
        """测试深度模式配置"""
        config = _get_depth_config("deep")
        assert config["rounds"] == 3
        assert config["min_sources"] == 30
        assert config["max_sources"] == 50

    def test_get_depth_config_default(self):
        """测试默认配置"""
        config = _get_depth_config("unknown")
        assert config == _get_depth_config("standard")

    def test_extract_search_queries_from_strings(self):
        """测试从字符串列表提取查询"""
        queries = ["query1", "query2", "query3"]
        result = _extract_search_queries({"search_queries": queries})
        assert result == queries

    def test_extract_search_queries_from_dicts(self):
        """测试从字典列表提取查询"""
        queries_data = [
            {"query": "query1", "purpose": "test"},
            {"query": "query2", "purpose": "test2"}
        ]
        result = _extract_search_queries({"search_queries": queries_data})
        assert result == ["query1", "query2"]

    def test_extract_search_queries_mixed(self):
        """测试混合类型提取"""
        queries_data = [
            "direct_query",
            {"query": "dict_query", "purpose": "test"}
        ]
        result = _extract_search_queries({"search_queries": queries_data})
        assert result == ["direct_query", "dict_query"]

    def test_extract_search_queries_empty(self):
        """测试空查询"""
        result = _extract_search_queries({})
        assert result == []

    def test_extract_search_queries_missing_key(self):
        """测试缺少search_queries键"""
        result = _extract_search_queries({"other_key": "value"})
        assert result == []
