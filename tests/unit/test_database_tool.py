"""Unit tests for DatabaseTool."""
import pytest
from unittest.mock import Mock, patch
from agent.tools.database_tool import DatabaseTool


@pytest.mark.unit
class TestDatabaseTool:
    """Unit tests for DatabaseTool."""
    
    def test_init(self, mock_config):
        """Test DatabaseTool initialization."""
        tool = DatabaseTool()
        assert tool.article_hashes == {}
        assert tool.user_history == {}
    
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
    
    def test_check_article_hash_not_exists(self, mock_config):
        """Test checking non-existent article hash."""
        tool = DatabaseTool()
        assert tool.check_article_hash("nonexistent_hash") is False
    
    def test_check_article_hash_exists(self, mock_config):
        """Test checking existing article hash."""
        tool = DatabaseTool()
        article = {"title": "Test", "url": "https://example.com"}
        article_hash = tool.get_article_hash(article)
        tool.store_article(article, article_hash)
        
        assert tool.check_article_hash(article_hash) is True
    
    def test_check_user_history_not_exists(self, mock_config):
        """Test checking user history for non-existent user."""
        tool = DatabaseTool()
        assert tool.check_user_history("user@example.com", "article_id") is False
    
    def test_check_user_history_exists(self, mock_config):
        """Test checking user history for existing entry."""
        tool = DatabaseTool()
        user_email = "user@example.com"
        article_id = "article_123"
        
        tool.mark_sent_to_user(user_email, article_id)
        assert tool.check_user_history(user_email, article_id) is True
    
    def test_store_article(self, mock_config):
        """Test storing article."""
        tool = DatabaseTool()
        article = {"title": "Test", "url": "https://example.com"}
        article_hash = tool.get_article_hash(article)
        
        tool.store_article(article, article_hash)
        assert tool.check_article_hash(article_hash) is True
    
    def test_mark_sent_to_user(self, mock_config):
        """Test marking article as sent to user."""
        tool = DatabaseTool()
        user_email = "user@example.com"
        article_id = "article_123"
        
        tool.mark_sent_to_user(user_email, article_id)
        assert user_email in tool.user_history
        assert article_id in tool.user_history[user_email]
    
    def test_deduplication_workflow(self, mock_config):
        """Test complete deduplication workflow."""
        tool = DatabaseTool()
        article = {"title": "Test", "url": "https://example.com"}
        article_hash = tool.get_article_hash(article)
        article_id = article["url"]
        user_email = "user@example.com"
        
        # First time: should not be duplicate
        assert tool.check_article_hash(article_hash) is False
        assert tool.check_user_history(user_email, article_id) is False
        
        # Store and mark as sent
        tool.store_article(article, article_hash)
        tool.mark_sent_to_user(user_email, article_id)
        
        # Second time: should be duplicate
        assert tool.check_article_hash(article_hash) is True
        assert tool.check_user_history(user_email, article_id) is True
