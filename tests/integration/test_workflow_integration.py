"""Integration tests for workflow nodes."""
import pytest
from unittest.mock import Mock, patch, MagicMock
from agent.workflow import BriefingAgentWorkflow
from agent.state import AgentState


@pytest.mark.integration
class TestWorkflowIntegration:
    """Integration tests for workflow nodes."""
    
    @patch('agent.tools.tavily_tool.TavilyClient')
    @patch('agent.tools.groq_tool.ChatGroq')
    def test_calendar_check_node(self, mock_groq_class, mock_tavily_class, mock_config, sample_agent_state):
        """Test calendar check node."""
        mock_tavily_client = Mock()
        mock_tavily_class.return_value = mock_tavily_client
        
        mock_llm = Mock()
        mock_groq_class.return_value = mock_llm
        
        workflow = BriefingAgentWorkflow()
        state = workflow.calendar_check_node(sample_agent_state.copy())
        
        assert "metadata" in state
        assert "calendar_check_passed" in state["metadata"]
    
    @patch('agent.tools.tavily_tool.TavilyClient')
    @patch('agent.tools.groq_tool.ChatGroq')
    def test_query_analysis_node(self, mock_groq_class, mock_tavily_class, mock_config, sample_agent_state):
        """Test query analysis node."""
        mock_tavily_client = Mock()
        mock_tavily_class.return_value = mock_tavily_client
        
        mock_llm = Mock()
        mock_response = Mock()
        mock_response.content = "AI news\ntechnology trends"
        mock_llm.invoke.return_value = mock_response
        mock_groq_class.return_value = mock_llm
        
        workflow = BriefingAgentWorkflow()
        state = workflow.query_analysis_node(sample_agent_state.copy())
        
        assert len(state["search_queries"]) > 0
        assert "metadata" in state
    
    @patch('agent.tools.tavily_tool.TavilyClient')
    @patch('agent.tools.groq_tool.ChatGroq')
    def test_search_node(self, mock_groq_class, mock_tavily_class, mock_config, sample_agent_state, sample_articles):
        """Test search node."""
        mock_tavily_client = Mock()
        mock_tavily_class.return_value = mock_tavily_client
        mock_tavily_client.search.return_value = {"results": sample_articles}
        
        mock_llm = Mock()
        mock_groq_class.return_value = mock_llm
        
        workflow = BriefingAgentWorkflow()
        state = sample_agent_state.copy()
        state["search_queries"] = ["AI technology"]
        state = workflow.search_node(state)
        
        assert len(state["articles"]) > 0
        assert "metadata" in state
    
    @patch('agent.tools.tavily_tool.TavilyClient')
    @patch('agent.tools.groq_tool.ChatGroq')
    def test_deduplication_node(self, mock_groq_class, mock_tavily_class, mock_config, sample_agent_state, sample_articles):
        """Test deduplication node."""
        mock_tavily_client = Mock()
        mock_tavily_class.return_value = mock_tavily_client
        
        mock_llm = Mock()
        mock_groq_class.return_value = mock_llm
        
        workflow = BriefingAgentWorkflow()
        state = sample_agent_state.copy()
        state["articles"] = sample_articles
        state = workflow.deduplication_node(state)
        
        assert len(state["deduplicated_articles"]) >= 0
        assert "metadata" in state
    
    @patch('agent.tools.tavily_tool.TavilyClient')
    @patch('agent.tools.groq_tool.ChatGroq')
    def test_summarize_node(self, mock_groq_class, mock_tavily_class, mock_config, sample_agent_state, sample_articles):
        """Test summarize node."""
        mock_tavily_client = Mock()
        mock_tavily_class.return_value = mock_tavily_client
        
        mock_llm = Mock()
        mock_response = Mock()
        mock_response.content = "TLDR: Test summary"
        mock_llm.invoke.return_value = mock_response
        mock_groq_class.return_value = mock_llm
        
        workflow = BriefingAgentWorkflow()
        state = sample_agent_state.copy()
        state["deduplicated_articles"] = sample_articles
        for article in state["deduplicated_articles"]:
            article["article_id"] = article["url"]
            article["article_hash"] = "test_hash"
        
        state = workflow.summarize_node(state)
        
        assert len(state["summaries"]) > 0
        assert "metadata" in state
    
    @patch('agent.tools.tavily_tool.TavilyClient')
    @patch('agent.tools.groq_tool.ChatGroq')
    def test_store_node(self, mock_groq_class, mock_tavily_class, mock_config, sample_agent_state, sample_summaries):
        """Test store node."""
        mock_tavily_client = Mock()
        mock_tavily_class.return_value = mock_tavily_client
        
        mock_llm = Mock()
        mock_groq_class.return_value = mock_llm
        
        workflow = BriefingAgentWorkflow()
        state = sample_agent_state.copy()
        state["summaries"] = sample_summaries
        state = workflow.store_node(state)
        
        assert "metadata" in state
        assert "articles_stored" in state["metadata"]
    
    @patch('agent.tools.tavily_tool.TavilyClient')
    @patch('agent.tools.groq_tool.ChatGroq')
    def test_format_node(self, mock_groq_class, mock_tavily_class, mock_config, sample_agent_state, sample_summaries):
        """Test format node."""
        mock_tavily_client = Mock()
        mock_tavily_class.return_value = mock_tavily_client
        
        mock_llm = Mock()
        mock_response = Mock()
        mock_response.content = "<html><body>Email content</body></html>"
        mock_llm.invoke.return_value = mock_response
        mock_groq_class.return_value = mock_llm
        
        workflow = BriefingAgentWorkflow()
        state = sample_agent_state.copy()
        state["summaries"] = sample_summaries
        state = workflow.format_node(state)
        
        assert len(state["email_content"]) > 0
        assert "metadata" in state
    
    @patch('agent.tools.tavily_tool.TavilyClient')
    @patch('agent.tools.groq_tool.ChatGroq')
    def test_email_node(self, mock_groq_class, mock_tavily_class, mock_config, sample_agent_state, sample_summaries):
        """Test email node."""
        mock_tavily_client = Mock()
        mock_tavily_class.return_value = mock_tavily_client
        
        mock_llm = Mock()
        mock_groq_class.return_value = mock_llm
        
        workflow = BriefingAgentWorkflow()
        state = sample_agent_state.copy()
        state["summaries"] = sample_summaries
        state["email_content"] = "<html><body>Test email</body></html>"
        state = workflow.email_node(state)
        
        assert "metadata" in state
        assert "email_sent" in state["metadata"]
