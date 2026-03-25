"""搜索服务单元测试"""
import pytest
from unittest.mock import Mock, patch
from app.services.search import SearchService, SearchError


@pytest.fixture
def mock_tavily_client():
    """模拟Tavily客户端"""
    with patch("app.services.search.TavilyClient") as mock:
        client_instance = Mock()
        client_instance.search.return_value = {
            "results": [
                {
                    "url": "https://example.com/1",
                    "title": "Test Article",
                    "content": "Test content",
                    "score": 0.9
                }
            ]
        }
        mock.return_value = client_instance
        yield mock


@pytest.mark.asyncio
async def test_search_service_init():
    """测试搜索服务初始化"""
    with pytest.raises(ValueError):
        SearchService(api_key=None)


@pytest.mark.asyncio
async def test_search_success(mock_tavily_client):
    """测试搜索成功"""
    service = SearchService(api_key="test-key")
    
    results = await service.search("test query", max_results=5)
    
    assert isinstance(results, list)
    assert len(results) == 1
    assert results[0]["url"] == "https://example.com/1"


@pytest.mark.asyncio
async def test_batch_search(mock_tavily_client):
    """测试批量搜索"""
    service = SearchService(api_key="test-key")
    
    queries = ["query1", "query2"]
    results = await service.batch_search(queries, max_results_per_query=3)
    
    assert "query1" in results
    assert "query2" in results
