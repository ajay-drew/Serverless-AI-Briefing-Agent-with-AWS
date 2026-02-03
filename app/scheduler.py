"""APScheduler configuration for scheduled briefings."""
import logging
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.jobstores.memory import MemoryJobStore
import pytz
from database import db_manager, User
from app.agent_runner import agent_runner

logger = logging.getLogger(__name__)

# Global scheduler instance
scheduler = AsyncIOScheduler(
    jobstores={'default': MemoryJobStore()},
    timezone=pytz.utc
)


def send_briefing(user_email: str):
    """
    Send scheduled briefing to a user.
    
    Args:
        user_email: User email address
    """
    logger.info(f"Scheduler triggering briefing for: {user_email}")
    
    try:
        result = agent_runner.run_scheduled_briefing(user_email)
        
        if result.get("success"):
            logger.info(f"✓ Scheduled briefing sent to {user_email}: {result.get('articles_sent', 0)} articles")
        else:
            logger.error(f"✗ Scheduled briefing failed for {user_email}: {result.get('error', 'Unknown error')}")
    
    except Exception as e:
        logger.error(f"Error in send_briefing for {user_email}: {str(e)}", exc_info=True)


def schedule_user_briefing(user_email: str, timezone: str, time: str) -> bool:
    """
    Schedule daily briefing for a user.
    
    Args:
        user_email: User email address
        timezone: User timezone (e.g., 'America/New_York')
        time: Briefing time in HH:MM format (e.g., '09:00')
        
    Returns:
        True if scheduling successful, False otherwise
    """
    try:
        # Parse time
        hour, minute = map(int, time.split(':'))
        
        # Create job ID
        job_id = f"briefing_{user_email}"
        
        # Remove existing job if any
        if scheduler.get_job(job_id):
            scheduler.remove_job(job_id)
            logger.info(f"Removed existing job: {job_id}")
        
        # Create cron trigger with user's timezone
        trigger = CronTrigger(
            hour=hour,
            minute=minute,
            timezone=pytz.timezone(timezone)
        )
        
        # Add job
        scheduler.add_job(
            send_briefing,
            trigger=trigger,
            args=[user_email],
            id=job_id,
            name=f"Daily briefing for {user_email}",
            replace_existing=True
        )
        
        logger.info(f"Scheduled briefing for {user_email} at {time} {timezone}")
        return True
        
    except Exception as e:
        logger.error(f"Error scheduling briefing for {user_email}: {str(e)}")
        return False


def unschedule_user_briefing(user_email: str) -> bool:
    """
    Unschedule briefing for a user.
    
    Args:
        user_email: User email address
        
    Returns:
        True if unscheduling successful, False otherwise
    """
    try:
        job_id = f"briefing_{user_email}"
        
        if scheduler.get_job(job_id):
            scheduler.remove_job(job_id)
            logger.info(f"Unscheduled briefing for {user_email}")
            return True
        else:
            logger.warning(f"No scheduled briefing found for {user_email}")
            return False
            
    except Exception as e:
        logger.error(f"Error unscheduling briefing for {user_email}: {str(e)}")
        return False


def load_all_scheduled_briefings():
    """Load all users from database and schedule their briefings."""
    logger.info("Loading scheduled briefings from database...")
    
    try:
        session = db_manager.get_session()
        users = session.query(User).all()
        session.close()
        
        scheduled_count = 0
        for user in users:
            success = schedule_user_briefing(
                user.email,
                user.timezone,
                user.briefing_time
            )
            if success:
                scheduled_count += 1
        
        logger.info(f"✓ Loaded {scheduled_count} scheduled briefings from database")
        
    except Exception as e:
        logger.error(f"Error loading scheduled briefings: {str(e)}")


def start_scheduler():
    """Start the scheduler and load all scheduled briefings."""
    if not scheduler.running:
        scheduler.start()
        logger.info("APScheduler started")
        
        # Load all scheduled briefings from database
        load_all_scheduled_briefings()
    else:
        logger.warning("Scheduler already running")


def shutdown_scheduler():
    """Shutdown the scheduler gracefully."""
    if scheduler.running:
        scheduler.shutdown(wait=True)
        logger.info("APScheduler shutdown complete")
    else:
        logger.warning("Scheduler not running")


def get_scheduled_jobs():
    """
    Get list of all scheduled jobs.
    
    Returns:
        List of job information dictionaries
    """
    jobs = []
    for job in scheduler.get_jobs():
        jobs.append({
            "id": job.id,
            "name": job.name,
            "next_run_time": job.next_run_time.isoformat() if job.next_run_time else None,
            "trigger": str(job.trigger),
        })
    return jobs
