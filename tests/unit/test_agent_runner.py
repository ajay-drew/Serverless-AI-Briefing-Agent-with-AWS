"""Unit tests for AgentRunner module."""
import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime


@pytest.mark.unit
class TestAgentRunner:
    """Unit tests for AgentRunner."""
    
    @pytest.fixture
    def mock_agent(self):
        """Mock LangGraph agent."""
        agent = MagicMock()
        agent.invoke = MagicMock()
        return agent
    
    @pytest.fixture
    def mock_db_session(self):
        """Mock database session."""
        session = MagicMock()
        session.query = MagicMock()
        session.close = MagicMock()
        return session
    
    def test_agent_runner_init(self):
        """Test AgentRunner initialization."""
        with patch('app.agent_runner.create_agent'):
            from app.agent_runner import AgentRunner
            
            runner = AgentRunner()
            assert runner.agent is not None
    
    def test_run_scheduled_briefing_success(self, mock_agent, mock_db_session):
        """Test running scheduled briefing successfully."""
        with patch('app.agent_runner.create_agent', return_value=mock_agent), \
             patch('app.agent_runner.db_manager.get_session', return_value=mock_db_session):
            
            from app.agent_runner import AgentRunner
            
            # Mock user
            mock_user = Mock()
            mock_user.email = "test@example.com"
            mock_user.preferences = {"topics": ["AI"]}
            mock_user.timezone = "UTC"
            mock_user.briefing_time = "09:00"
            mock_db_session.query().filter().first.return_value = mock_user
            
            # Mock agent result
            mock_agent.invoke.return_value = {
                "user_email": "test@example.com",
                "articles": [{"title": "Test"}],
                "summaries": [{"title": "Test", "summary": "Test summary"}],
                "errors": [],
                "metadata": {"email_sent": True}
            }
            
            runner = AgentRunner()
            result = runner.run_scheduled_briefing("test@example.com")
            
            assert result["success"] is True
            assert result["articles_sent"] == 1
            assert result["email_sent"] is True
    
    def test_run_scheduled_briefing_user_not_found(self, mock_agent, mock_db_session):
        """Test running briefing for non-existent user."""
        with patch('app.agent_runner.create_agent', return_value=mock_agent), \
             patch('app.agent_runner.db_manager.get_session', return_value=mock_db_session):
            
            from app.agent_runner import AgentRunner
            
            mock_db_session.query().filter().first.return_value = None
            
            runner = AgentRunner()
            result = runner.run_scheduled_briefing("nonexistent@example.com")
            
            assert result["success"] is False
            assert "not found" in result["error"]
    
    def test_run_scheduled_briefing_workflow_error(self, mock_agent, mock_db_session):
        """Test handling workflow errors."""
        with patch('app.agent_runner.create_agent', return_value=mock_agent), \
             patch('app.agent_runner.db_manager.get_session', return_value=mock_db_session):
            
            from app.agent_runner import AgentRunner
            
            # Mock user
            mock_user = Mock()
            mock_user.email = "test@example.com"
            mock_user.preferences = {"topics": ["AI"]}
            mock_user.timezone = "UTC"
            mock_user.briefing_time = "09:00"
            mock_db_session.query().filter().first.return_value = mock_user
            
            # Mock agent error
            mock_agent.invoke.side_effect = Exception("Workflow error")
            
            runner = AgentRunner()
            result = runner.run_scheduled_briefing("test@example.com")
            
            assert result["success"] is False
            assert "Workflow error" in result["error"]
    
    def test_run_real_time_query_success(self, mock_agent):
        """Test running real-time query successfully."""
        with patch('app.agent_runner.create_agent', return_value=mock_agent), \
             patch('app.agent_runner.db_manager.get_session') as mock_get_session:
            
            from app.agent_runner import AgentRunner
            
            # Mock database session (user not found, guest user)
            mock_session = MagicMock()
            mock_session.query().filter().first.return_value = None
            mock_get_session.return_value = mock_session
            
            # Mock agent result
            mock_agent.invoke.return_value = {
                "articles": [{"title": f"Article {i}"} for i in range(10)],
                "summaries": [
                    {"title": f"Article {i}", "url": f"http://test{i}.com", "summary": f"Summary {i}"}
                    for i in range(10)
                ],
                "errors": []
            }
            
            runner = AgentRunner()
            result = runner.run_real_time_query(
                "guest@example.com",
                "AI news",
                max_results=5
            )
            
            assert result["success"] is True
            assert len(result["articles"]) == 5  # Limited by max_results
            assert result["total_found"] == 10
    
    def test_run_real_time_query_with_registered_user(self, mock_agent, mock_db_session):
        """Test real-time query with registered user."""
        with patch('app.agent_runner.create_agent', return_value=mock_agent), \
             patch('app.agent_runner.db_manager.get_session', return_value=mock_db_session):
            
            from app.agent_runner import AgentRunner
            
            # Mock registered user
            mock_user = Mock()
            mock_user.preferences = {"topics": ["AI", "tech"]}
            mock_user.timezone = "UTC"
            mock_user.briefing_time = "09:00"
            mock_db_session.query().filter().first.return_value = mock_user
            
            # Mock agent result
            mock_agent.invoke.return_value = {
                "articles": [{"title": "Test"}],
                "summaries": [{"title": "Test", "url": "http://test.com", "summary": "Summary"}],
                "errors": []
            }
            
            runner = AgentRunner()
            result = runner.run_real_time_query(
                "registered@example.com",
                "machine learning",
                max_results=5
            )
            
            assert result["success"] is True
            assert result["query"] == "machine learning"
    
    def test_run_real_time_query_with_custom_preferences(self, mock_agent):
        """Test real-time query with custom preferences."""
        with patch('app.agent_runner.create_agent', return_value=mock_agent):
            from app.agent_runner import AgentRunner
            
            # Mock agent result
            mock_agent.invoke.return_value = {
                "articles": [],
                "summaries": [],
                "errors": []
            }
            
            custom_prefs = {
                "topics": ["custom topic"],
                "timezone": "America/New_York",
                "schedule_time": "10:00"
            }
            
            runner = AgentRunner()
            result = runner.run_real_time_query(
                "test@example.com",
                "test query",
                user_preferences=custom_prefs
            )
            
            assert result["success"] is True
            # Verify agent was called with custom preferences
            call_args = mock_agent.invoke.call_args[0][0]
            assert call_args["user_preferences"] == custom_prefs
    
    def test_run_real_time_query_error(self, mock_agent):
        """Test handling errors in real-time query."""
        with patch('app.agent_runner.create_agent', return_value=mock_agent), \
             patch('app.agent_runner.db_manager.get_session') as mock_get_session:
            
            from app.agent_runner import AgentRunner
            
            # Mock database error
            mock_session = MagicMock()
            mock_session.query().filter().first.side_effect = Exception("Database error")
            mock_get_session.return_value = mock_session
            
            runner = AgentRunner()
            result = runner.run_real_time_query(
                "test@example.com",
                "test query"
            )
            
            assert result["success"] is False
            assert "error" in result
            assert result["articles"] == []
