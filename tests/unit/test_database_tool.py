"""Unit tests for DatabaseTool."""
import pytest
from unittest.mock import Mock, MagicMock, patch
from agent.tools.database_tool import DatabaseTool
from database import Article, UserArticle


@pytest.mark.unit
class TestDatabaseTool:
    """Unit tests for DatabaseTool with mocked SQLAlchemy sessions."""
    
    @pytest.fixture
    def mock_session(self):
        """Create a mock database session."""
        session = MagicMock()
        session.query = MagicMock()
        session.add = MagicMock()
        session.commit = MagicMock()
        session.rollback = MagicMock()
        session.close = MagicMock()
        return session
    
    def test_init(self, mock_config):
        """Test DatabaseTool initialization."""
        tool = DatabaseTool()
        assert not tool.use_external_session
    
    def test_generate_article_hash(self, mock_config):
        """Test article hash generation."""
        tool = DatabaseTool()
        article = {
            "title": "Test Article",
            "url": "https://example.com/test"
        }
        hash1 = tool.get_article_hash(article)
        hash2 = tool.get_article_hash(article)
        
        # Same article should produce same hash
        assert hash1 == hash2
        assert len(hash1) == 64  # SHA256 produces 64 char hex string
    
    def test_check_article_hash_not_exists(self, mock_config, mock_session):
        """Test checking non-existent article hash."""
        mock_session.query().filter().first.return_value = None
        
        tool = DatabaseTool(session=mock_session)
        assert tool.check_article_hash("nonexistent_hash") is False
    
    def test_check_article_hash_exists(self, mock_config, mock_session):
        """Test checking existing article hash."""
        mock_article = Mock(spec=Article)
        mock_session.query().filter().first.return_value = mock_article
        
        tool = DatabaseTool(session=mock_session)
        assert tool.check_article_hash("existing_hash") is True
    
    def test_check_user_history_not_exists(self, mock_config, mock_session):
        """Test checking user history for non-existent user."""
        mock_session.query().filter().first.return_value = None
        
        tool = DatabaseTool(session=mock_session)
        assert tool.check_user_history("user@example.com", "article_id") is False
    
    def test_check_user_history_exists(self, mock_config, mock_session):
        """Test checking user history for existing entry."""
        mock_user_article = Mock(spec=UserArticle)
        mock_session.query().filter().first.return_value = mock_user_article
        
        tool = DatabaseTool(session=mock_session)
        assert tool.check_user_history("user@example.com", "article_id") is True
    
    def test_store_article(self, mock_config, mock_session):
        """Test storing article."""
        mock_session.query().filter().first.return_value = None  # Article doesn't exist
        
        tool = DatabaseTool(session=mock_session)
        article = {"title": "Test", "url": "https://example.com"}
        article_hash = tool.get_article_hash(article)
        
        tool.store_article(article, article_hash)
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
    
    def test_store_article_already_exists(self, mock_config, mock_session):
        """Test storing article that already exists."""
        mock_article = Mock(spec=Article)
        mock_session.query().filter().first.return_value = mock_article
        
        tool = DatabaseTool(session=mock_session)
        article = {"title": "Test", "url": "https://example.com"}
        article_hash = tool.get_article_hash(article)
        
        tool.store_article(article, article_hash)
        mock_session.add.assert_not_called()  # Should not add duplicate
    
    def test_mark_sent_to_user(self, mock_config, mock_session):
        """Test marking article as sent to user."""
        mock_session.query().filter().first.return_value = None  # Not marked yet
        
        tool = DatabaseTool(session=mock_session)
        tool.mark_sent_to_user("user@example.com", "article_123")
        
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
    
    def test_get_user_preferences(self, mock_config, mock_session):
        """Test getting user preferences."""
        mock_user = Mock()
        mock_user.preferences = {"topics": ["AI", "tech"]}
        mock_user.timezone = "America/New_York"
        mock_user.briefing_time = "09:00"
        mock_session.query().filter().first.return_value = mock_user
        
        tool = DatabaseTool(session=mock_session)
        prefs = tool.get_user_preferences("user@example.com")
        
        assert prefs is not None
        assert prefs["topics"] == ["AI", "tech"]
        assert prefs["timezone"] == "America/New_York"
        assert prefs["schedule_time"] == "09:00"
    
    def test_get_user_preferences_not_found(self, mock_config, mock_session):
        """Test getting preferences for non-existent user."""
        mock_session.query().filter().first.return_value = None
        
        tool = DatabaseTool(session=mock_session)
        prefs = tool.get_user_preferences("nonexistent@example.com")
        
        assert prefs is None
    
    def test_save_user_preferences(self, mock_config, mock_session):
        """Test saving user preferences."""
        mock_session.query().filter().first.return_value = None  # New user
        
        tool = DatabaseTool(session=mock_session)
        result = tool.save_user_preferences(
            "user@example.com",
            {"topics": ["AI"]},
            "UTC",
            "09:00"
        )
        
        assert result is True
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
