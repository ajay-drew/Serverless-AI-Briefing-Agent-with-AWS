"""Integration tests for tool interactions."""
import pytest
from unittest.mock import Mock, patch, MagicMock
from agent.tools import TavilyTool, GroqTool, DatabaseTool, EmailTool, CalendarTool


@pytest.mark.integration
class TestToolIntegration:
    """Integration tests for tool interactions."""
    
    @patch('agent.tools.tavily_tool.TavilyClient')
    @patch('agent.tools.groq_tool.ChatGroq')
    def test_tavily_groq_integration(self, mock_groq, mock_tavily_class, mock_config, sample_articles):
        """Test Tavily and Groq tools working together."""
        # Setup Tavily mock
        mock_tavily_client = Mock()
        mock_tavily_class.return_value = mock_tavily_client
        mock_tavily_client.search.return_value = {"results": sample_articles}
        
        # Setup Groq mock
        mock_llm = Mock()
        mock_response = Mock()
        mock_response.content = "TLDR: Test summary"
        mock_llm.invoke.return_value = mock_response
        mock_groq.return_value = mock_llm
        
        # Test integration
        tavily = TavilyTool()
        groq = GroqTool()
        
        # Search for articles
        articles = tavily.search_news("AI technology")
        assert len(articles) == 2
        
        # Summarize articles
        for article in articles:
            summary = groq.summarize_article(article)
            assert isinstance(summary, str)
            assert len(summary) > 0
    
    def test_database_calendar_integration(self, mock_config):
        """Test Database and Calendar tools working together."""
        database = DatabaseTool()
        calendar = CalendarTool()
        
        # Validate time
        is_valid = calendar.validate_send_time("America/New_York", "09:00", tolerance_minutes=60)
        assert isinstance(is_valid, bool)
        
        # Store article
        article = {"title": "Test", "url": "https://example.com"}
        article_hash = database.get_article_hash(article)
        database.store_article(article, article_hash)
        
        # Check deduplication
        assert database.check_article_hash(article_hash) is True
    
    @patch('agent.tools.groq_tool.ChatGroq')
    def test_groq_database_integration(self, mock_groq_class, mock_config, sample_summaries):
        """Test Groq and Database tools working together."""
        # Setup Groq mock
        mock_llm = Mock()
        mock_response = Mock()
        mock_response.content = "<html><body>Email content</body></html>"
        mock_llm.invoke.return_value = mock_response
        mock_groq_class.return_value = mock_llm
        
        groq = GroqTool()
        database = DatabaseTool()
        
        # Generate email content
        html = groq.generate_email_content(sample_summaries, {})
        assert "<html" in html.lower()
        
        # Mark articles as sent
        for summary in sample_summaries:
            database.mark_sent_to_user("user@example.com", summary["article_id"])
        
        # Verify they're marked
        for summary in sample_summaries:
            assert database.check_user_history("user@example.com", summary["article_id"])
    
    @patch('agent.tools.tavily_tool.TavilyClient')
    @patch('agent.tools.groq_tool.ChatGroq')
    def test_full_tool_chain(self, mock_groq_class, mock_tavily_class, mock_config, sample_articles):
        """Test full tool chain: Tavily -> Groq -> Database -> Email."""
        # Setup mocks
        mock_tavily_client = Mock()
        mock_tavily_class.return_value = mock_tavily_client
        mock_tavily_client.search.return_value = {"results": sample_articles}
        
        mock_llm = Mock()
        mock_response = Mock()
        mock_response.content = "Test summary"
        mock_llm.invoke.return_value = mock_response
        mock_groq_class.return_value = mock_llm
        
        # Initialize tools
        tavily = TavilyTool()
        groq = GroqTool()
        database = DatabaseTool()
        email = EmailTool()
        
        # 1. Search for articles
        articles = tavily.search_news("AI")
        assert len(articles) > 0
        
        # 2. Deduplicate
        deduplicated = []
        for article in articles:
            article_hash = database.get_article_hash(article)
            if not database.check_article_hash(article_hash):
                deduplicated.append(article)
                database.store_article(article, article_hash)
        
        # 3. Summarize
        summaries = []
        for article in deduplicated:
            summary_text = groq.summarize_article(article)
            summaries.append({
                **article,
                "summary": summary_text
            })
        
        # 4. Generate email
        html = groq.generate_email_content(summaries, {})
        assert len(html) > 0
        
        # 5. Send email (mock)
        result = email.send_email("user@example.com", "Test Subject", html)
        assert result["status"] == "logged"
        
        # 6. Mark as sent
        for summary in summaries:
            database.mark_sent_to_user("user@example.com", summary["url"])
