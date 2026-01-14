"""State management and schemas for the LangGraph agent."""
from typing import TypedDict, List, Dict, Any, Optional


class AgentState(TypedDict):
    """State schema for the LangGraph agent workflow."""
    
    # User information
    user_email: str
    user_preferences: Dict[str, Any]  # topics, timezone, schedule_time
    
    # Workflow data
    search_queries: List[str]
    articles: List[Dict[str, Any]]  # Raw articles from Tavily
    deduplicated_articles: List[Dict[str, Any]]  # After deduplication
    summaries: List[Dict[str, Any]]  # Article + summary pairs
    email_content: str
    
    # Error handling
    errors: List[str]
    
    # Metadata
    metadata: Dict[str, Any]  # execution time, API usage, etc.
