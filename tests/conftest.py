"""Shared pytest fixtures for all tests."""
import pytest
import os
from unittest.mock import Mock, patch, MagicMock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base


@pytest.fixture
def mock_config():
    """Mock configuration for all tests."""
    with patch('config.config') as mock:
        mock.GROQ_API_KEY = "test_groq_key"
        mock.GROQ_MODEL = "test_model"
        mock.TAVILY_API_KEY = "test_tavily_key"
        mock.DATABASE_URL = "sqlite:///:memory:"
        mock.SMTP_ENABLED = False
        mock.SMTP_SERVER = "smtp.test.com"
        mock.SMTP_PORT = 587
        mock.SMTP_USERNAME = "test@test.com"
        mock.SMTP_PASSWORD = "test_password"
        mock.SMTP_FROM_EMAIL = "from@test.com"
        mock.TEST_EMAIL_RECIPIENT = "recipient@test.com"
        mock.FRONTEND_URL = "http://localhost:3000"
        yield mock


@pytest.fixture
def test_db_engine():
    """Create a test database engine using SQLite in-memory."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_db_session(test_db_engine):
    """Create a test database session."""
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_db_engine)
    session = SessionLocal()
    yield session
    session.close()


@pytest.fixture
def mock_groq_client():
    """Mock Groq client for testing."""
    mock_client = Mock()
    mock_completion = Mock()
    mock_completion.choices = [Mock(message=Mock(content="Test response"))]
    mock_client.chat.completions.create.return_value = mock_completion
    return mock_client


@pytest.fixture
def mock_tavily_client():
    """Mock Tavily client for testing."""
    mock_client = Mock()
    mock_client.search.return_value = {
        "results": [
            {
                "title": "Test Article",
                "url": "https://example.com/test",
                "content": "Test content",
                "published_date": "2024-01-01",
                "score": 0.95
            }
        ]
    }
    return mock_client


@pytest.fixture
def sample_article():
    """Sample article for testing."""
    return {
        "title": "Test Article",
        "url": "https://example.com/test",
        "content": "This is a test article content",
        "published_date": "2024-01-01",
        "score": 0.95
    }


@pytest.fixture
def sample_user_preferences():
    """Sample user preferences for testing."""
    return {
        "topics": ["artificial intelligence", "technology"],
        "timezone": "America/New_York",
        "schedule_time": "09:00"
    }


@pytest.fixture
def sample_agent_state():
    """Sample agent state for testing."""
    return {
        "user_email": "test@example.com",
        "user_preferences": {
            "topics": ["AI", "tech"],
            "timezone": "UTC",
            "schedule_time": "09:00"
        },
        "search_queries": [],
        "articles": [],
        "deduplicated_articles": [],
        "summaries": [],
        "email_content": "",
        "errors": [],
        "metadata": {}
    }
