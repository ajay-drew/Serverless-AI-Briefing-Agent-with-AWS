"""Main entry point for the AI Briefing Agent."""
import logging
from datetime import datetime
import pytz
from agent import create_agent
from agent.state import AgentState
from config import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def main():
    """Main function to run the agent."""
    logger.info("=" * 80)
    logger.info("AI Briefing Agent - Starting Workflow")
    logger.info("=" * 80)
    
    # Create agent
    app = create_agent()
    
    # Get user email from config or use default
    user_email = config.TEST_EMAIL_RECIPIENT or "user@example.com"
    
    # Log configuration status
    if not config.TEST_EMAIL_RECIPIENT:
        logger.warning("⚠ TEST_EMAIL_RECIPIENT not found in .env file - using default: user@example.com")
        logger.info("   To fix: Add TEST_EMAIL_RECIPIENT=your-email@example.com to your .env file")
    else:
        logger.info(f"✓ TEST_EMAIL_RECIPIENT loaded: {config.TEST_EMAIL_RECIPIENT}")
    
    if not config.SES_FROM_EMAIL:
        logger.warning("⚠ SES_FROM_EMAIL not found in .env file - using default: noreply@example.com")
        logger.info("   To fix: Add SES_FROM_EMAIL=noreply@yourdomain.com to your .env file")
    else:
        logger.info(f"✓ SES_FROM_EMAIL loaded: {config.SES_FROM_EMAIL}")
    
    # Get user preferences from environment or use defaults
    # For testing, set schedule_time to current time in user's timezone
    user_timezone = "America/New_York"
    tz = pytz.timezone(user_timezone)
    current_time_in_tz = datetime.now(tz)
    current_time_str = current_time_in_tz.strftime("%H:%M")
    
    # Sample initial state
    initial_state: AgentState = {
        "user_email": user_email,  # Use email from .env file
        "user_preferences": {
            "topics": ["artificial intelligence", "technology"],
            "timezone": user_timezone,
            "schedule_time": current_time_str,
        },
        "search_queries": [],
        "articles": [],
        "deduplicated_articles": [],
        "summaries": [],
        "email_content": "",
        "errors": [],
        "metadata": {},
    }
    
    logger.info(f"User Email: {initial_state['user_email']}")
    logger.info(f"Topics: {initial_state['user_preferences']['topics']}")
    logger.info(f"Timezone: {user_timezone}")
    logger.info(f"Scheduled Time: {current_time_str}")
    logger.info("-" * 80)
    
    try:
        # Run workflow
        final_state = app.invoke(initial_state)
        
        # Display results
        logger.info("\n" + "=" * 80)
        logger.info("WORKFLOW COMPLETED")
        logger.info("=" * 80)
        logger.info(f"Search Queries: {final_state.get('search_queries', [])}")
        logger.info(f"Articles Found: {len(final_state.get('articles', []))}")
        logger.info(f"Articles After Dedup: {len(final_state.get('deduplicated_articles', []))}")
        logger.info(f"Summaries Generated: {len(final_state.get('summaries', []))}")
        logger.info(f"Errors: {final_state.get('errors', [])}")
        
        if final_state.get('summaries'):
            logger.info("\nArticle Summaries:")
            for i, summary in enumerate(final_state['summaries'], 1):
                logger.info(f"\n{i}. {summary.get('title', 'N/A')}")
                logger.info(f"   {summary.get('summary', 'N/A')}")
                logger.info(f"   {summary.get('url', 'N/A')}")
        
        if final_state.get('email_content'):
            logger.info(f"\nEmail Content Length: {len(final_state['email_content'])} characters")
            logger.info(f"Email Preview: {final_state['email_content'][:300]}...")
        
        logger.info("\n" + "=" * 80)
        
        # Check if email was sent
        if final_state.get("metadata", {}).get("email_sent"):
            logger.info("✓ Email sent successfully!")
            if final_state.get("metadata", {}).get("email_message_id"):
                logger.info(f"Message ID: {final_state['metadata']['email_message_id']}")
        else:
            logger.info("⚠ Email was not sent (check errors above)")
        
        logger.info("Agent execution completed successfully!")
        logger.info("=" * 80)
        
    except Exception as e:
        logger.error(f"Workflow failed: {str(e)}", exc_info=True)
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
