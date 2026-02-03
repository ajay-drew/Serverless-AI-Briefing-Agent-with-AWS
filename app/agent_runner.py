"""Agent runner module for executing LangGraph workflows."""
import logging
from datetime import datetime
from typing import Dict, Any, Optional
import pytz
from agent import create_agent
from agent.state import AgentState
from database import db_manager, User

logger = logging.getLogger(__name__)


class AgentRunner:
    """Wrapper for running LangGraph agent workflows."""
    
    def __init__(self):
        """Initialize agent runner."""
        self.agent = create_agent()
        logger.info("AgentRunner initialized")
    
    def run_scheduled_briefing(self, user_email: str) -> Dict[str, Any]:
        """
        Run scheduled briefing for a user.
        
        Args:
            user_email: User email address
            
        Returns:
            Dictionary with workflow results
        """
        logger.info(f"Running scheduled briefing for: {user_email}")
        
        try:
            # Get user preferences from database
            session = db_manager.get_session()
            user = session.query(User).filter(User.email == user_email).first()
            session.close()
            
            if not user:
                logger.error(f"User not found: {user_email}")
                return {
                    "success": False,
                    "error": "User not found",
                    "user_email": user_email
                }
            
            # Get current time in user's timezone
            tz = pytz.timezone(user.timezone)
            current_time = datetime.now(tz)
            current_time_str = current_time.strftime("%H:%M")
            
            # Prepare initial state
            initial_state: AgentState = {
                "user_email": user_email,
                "user_preferences": {
                    "topics": user.preferences.get("topics", []),
                    "timezone": user.timezone,
                    "schedule_time": user.briefing_time,
                },
                "search_queries": [],
                "articles": [],
                "deduplicated_articles": [],
                "summaries": [],
                "email_content": "",
                "errors": [],
                "metadata": {},
            }
            
            # Run workflow
            final_state = self.agent.invoke(initial_state)
            
            # Check results
            success = final_state.get("metadata", {}).get("email_sent", False)
            
            result = {
                "success": success,
                "user_email": user_email,
                "articles_found": len(final_state.get("articles", [])),
                "articles_sent": len(final_state.get("summaries", [])),
                "errors": final_state.get("errors", []),
                "email_sent": success,
            }
            
            if success:
                logger.info(f"✓ Briefing sent to {user_email}: {result['articles_sent']} articles")
            else:
                logger.warning(f"⚠ Briefing failed for {user_email}: {result['errors']}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error running scheduled briefing: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "user_email": user_email
            }
    
    def run_real_time_query(
        self,
        user_email: str,
        query: str,
        max_results: int = 5,
        user_preferences: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Run real-time search query (bypass calendar check).
        
        Args:
            user_email: User email address
            query: Search query string
            max_results: Maximum number of results
            user_preferences: Optional user preferences. If None, loads from database.
            
        Returns:
            Dictionary with search results
        """
        logger.info(f"Running real-time query for: {user_email} - '{query}'")
        
        try:
            # Get user preferences if not provided
            if user_preferences is None:
                session = db_manager.get_session()
                user = session.query(User).filter(User.email == user_email).first()
                session.close()
                
                if user:
                    user_preferences = {
                        "topics": user.preferences.get("topics", []),
                        "timezone": user.timezone,
                        "schedule_time": user.briefing_time,
                    }
                else:
                    # Guest user (not registered)
                    user_preferences = {
                        "topics": [query],
                        "timezone": "UTC",
                        "schedule_time": "09:00",
                    }
            
            # Prepare initial state with custom query
            initial_state: AgentState = {
                "user_email": user_email,
                "user_preferences": user_preferences,
                "search_queries": [query],  # Directly set query, skip query analysis
                "articles": [],
                "deduplicated_articles": [],
                "summaries": [],
                "email_content": "",
                "errors": [],
                "metadata": {
                    "calendar_check_passed": True,  # Bypass calendar check
                    "real_time_query": True,
                },
            }
            
            # Run workflow
            final_state = self.agent.invoke(initial_state)
            
            # Format results
            articles = []
            for summary in final_state.get("summaries", [])[:max_results]:
                articles.append({
                    "title": summary.get("title", ""),
                    "url": summary.get("url", ""),
                    "summary": summary.get("summary", ""),
                })
            
            result = {
                "success": True,
                "query": query,
                "articles": articles,
                "total_found": len(final_state.get("articles", [])),
                "total_returned": len(articles),
                "errors": final_state.get("errors", []),
            }
            
            logger.info(f"✓ Real-time query completed: {len(articles)} articles returned")
            
            return result
            
        except Exception as e:
            logger.error(f"Error running real-time query: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "query": query,
                "articles": [],
            }


# Global agent runner instance
agent_runner = AgentRunner()
