"""搜索服务单元测试"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from app.services.search import SearchService, SearchError


class TestSearchService:
    """搜索服务测试类"""

    @pytest.fixture
    def mock_tavily_client(self):
        """模拟Tavily客户端"""
        with patch("app.services.search.TavilyClient") as mock:
            client_instance = Mock()
            client_instance.search.return_value = {
                "results": [
                    {
                        "url": "https://example.com/1",
                        "title": "Test Article 1",
                        "content": "This is test content about AI and healthcare.",
                        "score": 0.95
                    },
                    {
                        "url": "https://example.com/2",
                        "title": "Test Article 2",
                        "content": "Machine learning applications in medical diagnosis.",
                        "score": 0.88
                    }
                ]
            }
            mock.return_value = client_instance
            yield mock

    def test_search_service_init_without_key(self):
        """测试无API密钥初始化"""
        with pytest.raises(ValueError, match="TAVILY_API_KEY not configured"):
            SearchService(api_key=None)

    def test_search_service_init_with_key(self, mock_tavily_client):
        """测试带API密钥初始化"""
        service = SearchService(api_key="test-key-123")
        assert service.api_key == "test-key-123"
        assert service.client is not None

    @pytest.mark.asyncio
    async def test_search_success(self, mock_tavily_client):
        """测试搜索成功"""
        service = SearchService(api_key="test-key")

        results = await service.search(
            "AI healthcare",
            max_results=5,
            search_depth="advanced"
        )

        assert isinstance(results, list)
        assert len(results) == 2
        assert results[0]["url"] == "https://example.com/1"
        assert results[0]["title"] == "Test Article 1"
        assert results[0]["score"] == 0.95

    @pytest.mark.asyncio
    async def test_search_with_raw_content(self, mock_tavily_client):
        """测试包含原始内容的搜索"""
        service = SearchService(api_key="test-key")

        results = await service.search(
            "test query",
            max_results=10,
            include_raw_content=True
        )

        assert len(results) > 0
        # 验证结果包含raw_content字段
        assert "raw_content" in results[0]

    @pytest.mark.asyncio
    async def test_search_error_handling(self):
        """测试搜索错误处理"""
        with patch("app.services.search.TavilyClient") as mock:
            mock.side_effect = Exception("API Error")

            service = SearchService(api_key="test-key")

            with pytest.raises(SearchError, match="Search failed"):
                await service.search("test query")

    @pytest.mark.asyncio
    async def test_batch_search(self, mock_tavily_client):
        """测试批量搜索"""
        service = SearchService(api_key="test-key")

        queries = ["query1", "query2"]
        results = await service.batch_search(queries, max_results_per_query=3)

        assert "query1" in results
        assert "query2" in results
        assert isinstance(results["query1"], list)
        assert isinstance(results["query2"], list)

    @pytest.mark.asyncio
    async def test_batch_search_partial_failure(self, mock_tavily_client):
        """测试批量搜索部分失败"""
        service = SearchService(api_key="test-key")

        # 模拟一个查询失败
        async def side_effect(*args, **kwargs):
            if "fail" in kwargs.get("query", ""):
                raise Exception("Query failed")
            return {
                "results": [{
                    "url": "https://example.com/result",
                    "title": "Result",
                    "content": "Content",
                    "score": 0.9
                }]
            }

        mock_tavily_client.side_effect = side_effect

        results = await service.batch_search(
            ["success query", "fail query"],
            max_results_per_query=5
        )

        assert "success query" in results
        assert "fail query" in results
        assert isinstance(results["fail query"], list)  # 空列表


class TestSearchError:
    """搜索错误测试"""

    def test_search_error_inheritance(self):
        """测试SearchError异常继承"""
        error = SearchError("Test error")
        assert isinstance(error, Exception)
        assert str(error) == "Test error"

    def test_search_error_with_original_exception(self):
        """测试携带原始异常的错误"""
        original = ValueError("Original error")
        error = SearchError(f"Wrapped: {original}")
        assert "Wrapped" in str(error)
        assert "Original error" in str(error)
