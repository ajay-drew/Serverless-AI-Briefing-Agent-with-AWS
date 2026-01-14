"""Unit tests for TavilyTool."""
import pytest
from unittest.mock import Mock, patch, MagicMock
from agent.tools.tavily_tool import TavilyTool


@pytest.mark.unit
class TestTavilyTool:
    """Unit tests for TavilyTool."""
    
    def test_init_success(self, mock_config):
        """Test TavilyTool initialization with valid config."""
        tool = TavilyTool()
        assert tool.max_retries == 3
        assert tool.base_delay == 1
        assert tool.client is not None
    
    def test_init_missing_api_key(self):
        """Test TavilyTool initialization without API key."""
        with patch('config.config.TAVILY_API_KEY', ""):
            with pytest.raises(ValueError, match="TAVILY_API_KEY not configured"):
                TavilyTool()
    
    @patch('agent.tools.tavily_tool.TavilyClient')
    def test_search_news_success(self, mock_client_class, mock_config, sample_articles):
        """Test successful news search."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_client.search.return_value = {
            "results": sample_articles
        }
        
        tool = TavilyTool()
        results = tool.search_news("AI technology", max_results=5)
        
        assert len(results) == 2
        assert results[0]["title"] == "AI Breakthrough in Natural Language Processing"
        assert "url" in results[0]
        assert "content" in results[0]
        mock_client.search.assert_called_once()
    
    @patch('agent.tools.tavily_tool.TavilyClient')
    def test_search_news_empty_results(self, mock_client_class, mock_config):
        """Test search with empty results."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_client.search.return_value = {"results": []}
        
        tool = TavilyTool()
        results = tool.search_news("test query")
        
        assert results == []
    
    @patch('agent.tools.tavily_tool.TavilyClient')
    @patch('time.sleep')
    def test_search_news_retry_logic(self, mock_sleep, mock_client_class, mock_config):
        """Test retry logic on API failure."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_client.search.side_effect = [
            Exception("API Error"),
            Exception("API Error"),
            {"results": [{"title": "Success", "url": "https://example.com"}]}
        ]
        
        tool = TavilyTool()
        results = tool.search_news("test query")
        
        assert len(results) == 1
        assert mock_client.search.call_count == 3
        assert mock_sleep.call_count == 2  # Should sleep between retries
    
    @patch('agent.tools.tavily_tool.TavilyClient')
    @patch('time.sleep')
    def test_search_news_max_retries_exceeded(self, mock_sleep, mock_client_class, mock_config):
        """Test that exception is raised after max retries."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_client.search.side_effect = Exception("API Error")
        
        tool = TavilyTool()
        
        with pytest.raises(Exception, match="API Error"):
            tool.search_news("test query")
        
        assert mock_client.search.call_count == 3
        assert mock_sleep.call_count == 2
