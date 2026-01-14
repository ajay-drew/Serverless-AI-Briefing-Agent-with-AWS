"""Pytest configuration and shared fixtures."""
import pytest
import os
from unittest.mock import Mock, MagicMock, patch
from typing import Dict, Any
from agent.state import AgentState


@pytest.fixture(autouse=True)
def mock_config(monkeypatch):
    """Mock configuration for testing - patches config for all tools."""
    import config
    import agent.tools.tavily_tool
    import agent.tools.groq_tool
    import agent.tools.email_tool
    
    # Patch the config object directly (since tools import 'from config import config')
    monkeypatch.setattr(config.config, 'GROQ_API_KEY', "test_groq_key")
    monkeypatch.setattr(config.config, 'GROQ_MODEL', "llama-3.1-70b-versatile")
    monkeypatch.setattr(config.config, 'TAVILY_API_KEY', "test_tavily_key")
    monkeypatch.setattr(config.config, 'AWS_ACCESS_KEY_ID', "test_aws_key")
    monkeypatch.setattr(config.config, 'AWS_SECRET_ACCESS_KEY', "test_aws_secret")
    monkeypatch.setattr(config.config, 'AWS_REGION', "us-east-1")
    monkeypatch.setattr(config.config, 'SES_FROM_EMAIL', "test@example.com")
    monkeypatch.setattr(config.config, 'DYNAMODB_NEWS_ARTICLES_TABLE', "news_articles")
    monkeypatch.setattr(config.config, 'DYNAMODB_USER_SUMMARIES_TABLE', "user_summaries")
    monkeypatch.setattr(config.config, 'DYNAMODB_USER_PREFERENCES_TABLE', "user_preferences")
    
    # Also patch the config object in tool modules (they import it, so we need to patch the same object)
    monkeypatch.setattr(agent.tools.tavily_tool.config, 'TAVILY_API_KEY', "test_tavily_key")
    monkeypatch.setattr(agent.tools.groq_tool.config, 'GROQ_API_KEY', "test_groq_key")
    monkeypatch.setattr(agent.tools.groq_tool.config, 'GROQ_MODEL', "llama-3.1-70b-versatile")
    monkeypatch.setattr(agent.tools.email_tool.config, 'SES_FROM_EMAIL', "test@example.com")
    
    yield


@pytest.fixture
def sample_agent_state() -> AgentState:
    """Sample agent state for testing."""
    return {
        "user_email": "test@example.com",
        "user_preferences": {
            "topics": ["artificial intelligence", "technology"],
            "timezone": "America/New_York",
            "schedule_time": "09:00",
        },
        "search_queries": [],
        "articles": [],
        "deduplicated_articles": [],
        "summaries": [],
        "email_content": "",
        "errors": [],
        "metadata": {},
    }


@pytest.fixture
def sample_articles():
    """Sample articles from Tavily API."""
    return [
        {
            "title": "AI Breakthrough in Natural Language Processing",
            "url": "https://example.com/ai-breakthrough",
            "content": "Scientists have made significant progress...",
            "published_date": "2024-01-15",
            "score": 0.95,
            "raw_content": "Full article content here...",
        },
        {
            "title": "New Technology Trends for 2024",
            "url": "https://example.com/tech-trends",
            "content": "Technology continues to evolve rapidly...",
            "published_date": "2024-01-14",
            "score": 0.88,
            "raw_content": "Full article content here...",
        },
    ]


@pytest.fixture
def sample_summaries():
    """Sample article summaries."""
    return [
        {
            "title": "AI Breakthrough in Natural Language Processing",
            "url": "https://example.com/ai-breakthrough",
            "summary": "Scientists achieve major NLP milestone with new model architecture.",
            "article_id": "https://example.com/ai-breakthrough",
            "article_hash": "abc123",
        },
        {
            "title": "New Technology Trends for 2024",
            "url": "https://example.com/tech-trends",
            "summary": "Emerging technologies reshape industry landscape this year.",
            "article_id": "https://example.com/tech-trends",
            "article_hash": "def456",
        },
    ]


@pytest.fixture
def mock_tavily_client():
    """Mock Tavily client."""
    mock_client = Mock()
    mock_response = {
        "results": [
            {
                "title": "Test Article",
                "url": "https://example.com/test",
                "content": "Test content",
                "published_date": "2024-01-15",
                "score": 0.9,
                "raw_content": "Raw content",
            }
        ]
    }
    mock_client.search.return_value = mock_response
    return mock_client


@pytest.fixture
def mock_groq_llm():
    """Mock Groq LLM."""
    mock_llm = Mock()
    mock_response = Mock()
    mock_response.content = "Mock LLM response"
    mock_llm.invoke.return_value = mock_response
    return mock_llm
