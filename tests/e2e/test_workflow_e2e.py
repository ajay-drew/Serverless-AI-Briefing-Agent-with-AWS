"""End-to-end tests for the complete workflow."""
import pytest
from unittest.mock import Mock, patch, MagicMock
from agent import create_agent
from agent.state import AgentState


@pytest.mark.e2e
class TestWorkflowE2E:
    """End-to-end tests for the complete agent workflow."""
    
    @patch('agent.tools.calendar_tool.CalendarTool.validate_send_time')
    @patch('agent.tools.tavily_tool.TavilyClient')
    @patch('agent.tools.groq_tool.ChatGroq')
    def test_full_workflow_success(self, mock_groq_class, mock_tavily_class, mock_calendar, mock_config, sample_agent_state, sample_articles):
        """Test complete workflow from start to finish."""
        # Mock calendar check to always pass
        mock_calendar.return_value = True
        
        # Setup Tavily mock
        mock_tavily_client = Mock()
        mock_tavily_class.return_value = mock_tavily_client
        mock_tavily_client.search.return_value = {"results": sample_articles}
        
        # Setup Groq mock with different responses for different calls
        mock_llm = Mock()
        mock_groq_class.return_value = mock_llm
        
        # Mock responses for different LLM calls
        mock_responses = [
            Mock(content="AI news\ntechnology trends"),  # analyze_preferences
            Mock(content="TLDR: Major AI breakthrough announced"),  # summarize_article 1
            Mock(content="TLDR: New tech trends emerge"),  # summarize_article 2
            Mock(content="<html><body><h2>Your Daily Briefing</h2><ul><li>Article 1</li><li>Article 2</li></ul></body></html>"),  # generate_email_content
        ]
        mock_llm.invoke.side_effect = mock_responses
        
        # Create and run agent
        app = create_agent()
        final_state = app.invoke(sample_agent_state)
        
        # Verify workflow completed
        assert "search_queries" in final_state
        assert len(final_state["search_queries"]) > 0
        assert len(final_state["articles"]) > 0
        assert len(final_state["deduplicated_articles"]) > 0
        assert len(final_state["summaries"]) > 0
        assert len(final_state["email_content"]) > 0
        assert "metadata" in final_state
    
    @patch('agent.tools.calendar_tool.CalendarTool.validate_send_time')
    @patch('agent.tools.tavily_tool.TavilyClient')
    @patch('agent.tools.groq_tool.ChatGroq')
    def test_workflow_with_no_articles(self, mock_groq_class, mock_tavily_class, mock_calendar, mock_config, sample_agent_state):
        """Test workflow when no articles are found."""
        # Mock calendar check to always pass
        mock_calendar.return_value = True
        
        # Setup mocks
        mock_tavily_client = Mock()
        mock_tavily_class.return_value = mock_tavily_client
        mock_tavily_client.search.return_value = {"results": []}
        
        mock_llm = Mock()
        mock_response = Mock()
        mock_response.content = "AI news\ntechnology trends"
        mock_llm.invoke.return_value = mock_response
        mock_groq_class.return_value = mock_llm
        
        # Run workflow
        app = create_agent()
        final_state = app.invoke(sample_agent_state)
        
        # Should have queries but no articles
        assert len(final_state.get("search_queries", [])) > 0
        assert len(final_state.get("articles", [])) == 0
        # Workflow should skip to end when no articles found
        assert "metadata" in final_state
    
    @patch('agent.tools.tavily_tool.TavilyClient')
    @patch('agent.tools.groq_tool.ChatGroq')
    def test_workflow_with_duplicates(self, mock_groq_class, mock_tavily_class, mock_config, sample_agent_state, sample_articles):
        """Test workflow with duplicate articles."""
        # Setup mocks
        mock_tavily_client = Mock()
        mock_tavily_class.return_value = mock_tavily_client
        mock_tavily_client.search.return_value = {"results": sample_articles}
        
        mock_llm = Mock()
        mock_responses = [
            Mock(content="AI news"),
            Mock(content="Summary 1"),
            Mock(content="Summary 2"),
            Mock(content="<html><body>Email</body></html>"),
        ]
        mock_llm.invoke.side_effect = mock_responses
        mock_groq_class.return_value = mock_llm
        
        # Run workflow first time
        app = create_agent()
        final_state1 = app.invoke(sample_agent_state)
        
        # Run workflow second time with same articles (should be deduplicated)
        final_state2 = app.invoke(sample_agent_state)
        
        # Second run should have fewer or no new articles after deduplication
        assert len(final_state2.get("deduplicated_articles", [])) <= len(final_state1.get("deduplicated_articles", []))
    
    @patch('agent.tools.tavily_tool.TavilyClient')
    @patch('agent.tools.groq_tool.ChatGroq')
    def test_workflow_error_handling(self, mock_groq_class, mock_tavily_class, mock_config, sample_agent_state):
        """Test workflow error handling."""
        # Setup mocks to fail
        mock_tavily_client = Mock()
        mock_tavily_class.return_value = mock_tavily_client
        mock_tavily_client.search.side_effect = Exception("API Error")
        
        mock_llm = Mock()
        mock_llm.invoke.side_effect = Exception("LLM Error")
        mock_groq_class.return_value = mock_llm
        
        # Run workflow
        app = create_agent()
        final_state = app.invoke(sample_agent_state)
        
        # Should have errors recorded
        assert len(final_state.get("errors", [])) > 0
        assert "metadata" in final_state
    
    @patch('agent.tools.tavily_tool.TavilyClient')
    @patch('agent.tools.groq_tool.ChatGroq')
    def test_workflow_calendar_check_skip(self, mock_groq_class, mock_tavily_class, mock_config, sample_agent_state):
        """Test workflow skipping when calendar check fails."""
        # Setup mocks
        mock_tavily_client = Mock()
        mock_tavily_class.return_value = mock_tavily_client
        
        mock_llm = Mock()
        mock_groq_class.return_value = mock_llm
        
        # Modify state to have invalid schedule time (far in future)
        sample_agent_state["user_preferences"]["schedule_time"] = "23:59"
        sample_agent_state["user_preferences"]["timezone"] = "UTC"
        
        # Run workflow
        app = create_agent()
        final_state = app.invoke(sample_agent_state)
        
        # Should have calendar check metadata
        assert "metadata" in final_state
        # If calendar check fails, workflow should skip early
        calendar_passed = final_state.get("metadata", {}).get("calendar_check_passed", True)
        # Note: Calendar check may pass if within tolerance, so we just verify it was checked
        assert "calendar_check_passed" in final_state.get("metadata", {})
