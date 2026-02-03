"""Integration tests for database operations."""
import pytest
from datetime import datetime
from database import Base, User, Article, UserArticle, DatabaseManager
from agent.tools.database_tool import DatabaseTool


@pytest.mark.integration
class TestDatabaseIntegration:
    """Integration tests for database operations."""
    
    @pytest.fixture
    def db_manager(self):
        """Create test database manager with in-memory SQLite."""
        manager = DatabaseManager("sqlite:///:memory:")
        manager.create_tables()
        yield manager
        manager.drop_tables()
    
    @pytest.fixture
    def db_session(self, db_manager):
        """Create database session."""
        session = db_manager.get_session()
        yield session
        session.close()
    
    def test_create_user(self, db_session):
        """Test creating a user."""
        user = User(
            email="test@example.com",
            preferences={"topics": ["AI", "tech"]},
            timezone="UTC",
            briefing_time="09:00",
            created_at=datetime.utcnow()
        )
        
        db_session.add(user)
        db_session.commit()
        
        # Query back
        retrieved = db_session.query(User).filter(User.email == "test@example.com").first()
        assert retrieved is not None
        assert retrieved.timezone == "UTC"
        assert retrieved.preferences["topics"] == ["AI", "tech"]
    
    def test_create_article(self, db_session):
        """Test creating an article."""
        article = Article(
            id="test_hash_123",
            url_hash="test_hash_123",
            title="Test Article",
            url="https://example.com/test",
            summary="Test summary",
            created_at=datetime.utcnow()
        )
        
        db_session.add(article)
        db_session.commit()
        
        # Query back
        retrieved = db_session.query(Article).filter(Article.id == "test_hash_123").first()
        assert retrieved is not None
        assert retrieved.title == "Test Article"
    
    def test_create_user_article_relationship(self, db_session):
        """Test creating user-article relationship."""
        # Create user
        user = User(
            email="test@example.com",
            preferences={"topics": ["AI"]},
            timezone="UTC",
            briefing_time="09:00",
            created_at=datetime.utcnow()
        )
        db_session.add(user)
        
        # Create article
        article = Article(
            id="article_123",
            url_hash="article_123",
            title="Test",
            url="https://example.com",
            summary="Summary",
            created_at=datetime.utcnow()
        )
        db_session.add(article)
        db_session.commit()
        
        # Create relationship
        user_article = UserArticle(
            user_email="test@example.com",
            article_id="article_123",
            sent_at=datetime.utcnow()
        )
        db_session.add(user_article)
        db_session.commit()
        
        # Query back
        retrieved = db_session.query(UserArticle).filter(
            UserArticle.user_email == "test@example.com",
            UserArticle.article_id == "article_123"
        ).first()
        
        assert retrieved is not None
        assert retrieved.user_email == "test@example.com"
    
    def test_database_tool_integration(self, db_manager):
        """Test DatabaseTool with real database."""
        session = db_manager.get_session()
        tool = DatabaseTool(session=session)
        
        # Test article operations
        article = {"title": "Test Article", "url": "https://example.com/test"}
        article_hash = tool.get_article_hash(article)
        
        # First check - should not exist
        assert tool.check_article_hash(article_hash) is False
        
        # Store article
        tool.store_article(article, article_hash)
        
        # Second check - should exist
        assert tool.check_article_hash(article_hash) is True
        
        session.close()
    
    def test_database_tool_user_preferences(self, db_manager):
        """Test DatabaseTool user preferences operations."""
        session = db_manager.get_session()
        tool = DatabaseTool(session=session)
        
        # Save preferences
        success = tool.save_user_preferences(
            "test@example.com",
            {"topics": ["AI", "ML"]},
            "America/New_York",
            "09:00"
        )
        assert success is True
        
        # Retrieve preferences
        prefs = tool.get_user_preferences("test@example.com")
        assert prefs is not None
        assert prefs["topics"] == ["AI", "ML"]
        assert prefs["timezone"] == "America/New_York"
        
        session.close()
    
    def test_database_tool_deduplication_flow(self, db_manager):
        """Test complete deduplication flow."""
        session = db_manager.get_session()
        tool = DatabaseTool(session=session)
        
        # Create user
        user = User(
            email="user@example.com",
            preferences={"topics": ["AI"]},
            timezone="UTC",
            briefing_time="09:00",
            created_at=datetime.utcnow()
        )
        session.add(user)
        session.commit()
        
        # Test article
        article = {"title": "Test", "url": "https://example.com"}
        article_hash = tool.get_article_hash(article)
        article_id = article["url"]
        
        # Check - should not be duplicate
        assert tool.check_article_hash(article_hash) is False
        assert tool.check_user_history("user@example.com", article_id) is False
        
        # Store and mark as sent
        tool.store_article(article, article_hash)
        tool.mark_sent_to_user("user@example.com", article_id)
        
        # Check again - should be duplicate
        assert tool.check_article_hash(article_hash) is True
        assert tool.check_user_history("user@example.com", article_id) is True
        
        session.close()
    
    def test_cascade_delete_user(self, db_session):
        """Test cascade delete when user is deleted."""
        # Create user
        user = User(
            email="test@example.com",
            preferences={"topics": ["AI"]},
            timezone="UTC",
            briefing_time="09:00",
            created_at=datetime.utcnow()
        )
        db_session.add(user)
        
        # Create article
        article = Article(
            id="article_123",
            url_hash="article_123",
            title="Test",
            url="https://example.com",
            summary="Summary",
            created_at=datetime.utcnow()
        )
        db_session.add(article)
        db_session.commit()
        
        # Create relationship
        user_article = UserArticle(
            user_email="test@example.com",
            article_id="article_123",
            sent_at=datetime.utcnow()
        )
        db_session.add(user_article)
        db_session.commit()
        
        # Delete user
        db_session.delete(user)
        db_session.commit()
        
        # Check that user_article was also deleted (cascade)
        remaining = db_session.query(UserArticle).filter(
            UserArticle.user_email == "test@example.com"
        ).first()
        
        assert remaining is None
