"""Unit tests for GroqTool."""
import pytest
from unittest.mock import Mock, patch, MagicMock
from agent.tools.groq_tool import GroqTool


@pytest.mark.unit
class TestGroqTool:
    """Unit tests for GroqTool."""
    
    def test_init_success(self, mock_config):
        """Test GroqTool initialization with valid config."""
        with patch('agent.tools.groq_tool.ChatGroq') as mock_chatgroq:
            mock_llm = Mock()
            mock_chatgroq.return_value = mock_llm
            
            tool = GroqTool()
            assert tool.max_retries == 3
            assert tool.base_delay == 1
            mock_chatgroq.assert_called_once()
    
    def test_init_missing_api_key(self):
        """Test GroqTool initialization without API key."""
        with patch('config.config.GROQ_API_KEY', ""):
            with patch('agent.tools.groq_tool.ChatGroq') as mock_chatgroq:
                with pytest.raises(ValueError, match="GROQ_API_KEY not configured"):
                    GroqTool()
    
    @patch('agent.tools.groq_tool.ChatGroq')
    def test_analyze_preferences(self, mock_chatgroq_class, mock_config):
        """Test preference analysis."""
        mock_llm = Mock()
        mock_response = Mock()
        mock_response.content = "AI news\ntechnology trends"
        mock_llm.invoke.return_value = mock_response
        mock_chatgroq_class.return_value = mock_llm
        
        tool = GroqTool()
        preferences = {"topics": ["AI", "technology"]}
        queries = tool.analyze_preferences(preferences)
        
        assert isinstance(queries, list)
        assert len(queries) <= 2
        mock_llm.invoke.assert_called_once()
    
    @patch('agent.tools.groq_tool.ChatGroq')
    def test_analyze_preferences_empty_topics(self, mock_chatgroq_class, mock_config):
        """Test preference analysis with empty topics."""
        mock_llm = Mock()
        mock_chatgroq_class.return_value = mock_llm
        
        tool = GroqTool()
        preferences = {"topics": []}
        queries = tool.analyze_preferences(preferences)
        
        assert queries == []
    
    @patch('agent.tools.groq_tool.ChatGroq')
    def test_analyze_preferences_fallback(self, mock_chatgroq_class, mock_config):
        """Test preference analysis fallback on error."""
        mock_llm = Mock()
        mock_llm.invoke.side_effect = Exception("API Error")
        mock_chatgroq_class.return_value = mock_llm
        
        tool = GroqTool()
        preferences = {"topics": ["AI", "technology"]}
        queries = tool.analyze_preferences(preferences)
        
        # Should fallback to simple queries
        assert len(queries) == 2
        assert "AI" in queries[0] or "technology" in queries[0]
    
    @patch('agent.tools.groq_tool.ChatGroq')
    def test_summarize_article(self, mock_chatgroq_class, mock_config):
        """Test article summarization."""
        mock_llm = Mock()
        mock_response = Mock()
        mock_response.content = "TLDR: Major breakthrough in AI research"
        mock_llm.invoke.return_value = mock_response
        mock_chatgroq_class.return_value = mock_llm
        
        tool = GroqTool()
        article = {
            "title": "AI Breakthrough",
            "content": "Long article content here...",
            "url": "https://example.com"
        }
        summary = tool.summarize_article(article)
        
        assert isinstance(summary, str)
        assert len(summary) > 0
        mock_llm.invoke.assert_called_once()
    
    @patch('agent.tools.groq_tool.ChatGroq')
    def test_summarize_article_fallback(self, mock_chatgroq_class, mock_config):
        """Test article summarization fallback."""
        mock_llm = Mock()
        mock_llm.invoke.side_effect = Exception("API Error")
        mock_chatgroq_class.return_value = mock_llm
        
        tool = GroqTool()
        article = {"title": "Test Article", "content": "Content", "url": "https://example.com"}
        summary = tool.summarize_article(article)
        
        # Should fallback to title
        assert summary == "Test Article"
    
    @patch('agent.tools.groq_tool.ChatGroq')
    def test_generate_email_content(self, mock_chatgroq_class, mock_config, sample_summaries):
        """Test email content generation."""
        mock_llm = Mock()
        mock_response = Mock()
        mock_response.content = "<html><body><h2>Your Briefing</h2><p>Content</p></body></html>"
        mock_llm.invoke.return_value = mock_response
        mock_chatgroq_class.return_value = mock_llm
        
        tool = GroqTool()
        preferences = {"topics": ["AI"]}
        html = tool.generate_email_content(sample_summaries, preferences)
        
        assert isinstance(html, str)
        assert "<html" in html.lower() or "<body" in html.lower()
        mock_llm.invoke.assert_called_once()
    
    @patch('agent.tools.groq_tool.ChatGroq')
    def test_generate_email_content_empty_summaries(self, mock_chatgroq_class, mock_config):
        """Test email generation with empty summaries."""
        mock_llm = Mock()
        mock_chatgroq_class.return_value = mock_llm
        
        tool = GroqTool()
        html = tool.generate_email_content([], {})
        
        assert html == "<p>No new articles found today.</p>"
    
    @patch('agent.tools.groq_tool.ChatGroq')
    def test_generate_email_content_fallback(self, mock_chatgroq_class, mock_config, sample_summaries):
        """Test email generation fallback."""
        mock_llm = Mock()
        mock_llm.invoke.side_effect = Exception("API Error")
        mock_chatgroq_class.return_value = mock_llm
        
        tool = GroqTool()
        html = tool.generate_email_content(sample_summaries, {})
        
        # Should have fallback HTML structure
        assert "<html>" in html
        assert "<body>" in html
        assert "Your Daily Briefing" in html
