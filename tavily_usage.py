"""Tavily API usage tracking and rate limits (daily, weekly, monthly)."""
import logging
from datetime import datetime, timedelta
from database import db_manager, TavilyUsage

logger = logging.getLogger(__name__)

# Limits: 35/day, 245/week, 994/month (cap under 1000)
TAVILY_DAILY_LIMIT = 35
TAVILY_WEEKLY_LIMIT = 245
TAVILY_MONTHLY_LIMIT = 994


def _utc_now() -> datetime:
    """Current time in UTC (naive for DB compatibility)."""
    return datetime.utcnow()


def _start_of_day_utc(dt: datetime) -> datetime:
    """Start of day (00:00:00) in UTC for the given datetime."""
    return dt.replace(hour=0, minute=0, second=0, microsecond=0)


def _start_of_week_utc(dt: datetime) -> datetime:
    """Start of week (Monday 00:00:00) in UTC."""
    start_day = _start_of_day_utc(dt)
    return start_day - timedelta(days=dt.weekday())


def _start_of_month_utc(dt: datetime) -> datetime:
    """Start of month (1st 00:00:00) in UTC."""
    return dt.replace(day=1, hour=0, minute=0, second=0, microsecond=0)


def get_tavily_usage() -> tuple[int, int, int]:
    """
    Get current Tavily usage counts in UTC.
    Returns:
        (daily_count, weekly_count, monthly_count)
    """
    now = _utc_now()
    start_day = _start_of_day_utc(now)
    start_week = _start_of_week_utc(now)
    start_month = _start_of_month_utc(now)

    session = db_manager.get_session()
    try:
        daily = session.query(TavilyUsage).filter(TavilyUsage.used_at >= start_day).count()
        weekly = session.query(TavilyUsage).filter(TavilyUsage.used_at >= start_week).count()
        monthly = session.query(TavilyUsage).filter(TavilyUsage.used_at >= start_month).count()
        return (daily, weekly, monthly)
    finally:
        session.close()


def record_tavily_usage() -> None:
    """Record one Tavily search in the database (call after successful API call)."""
    session = db_manager.get_session()
    try:
        usage = TavilyUsage(used_at=_utc_now())
        session.add(usage)
        session.commit()
        logger.debug("Recorded Tavily usage")
    except Exception as e:
        session.rollback()
        logger.error(f"Failed to record Tavily usage: {e}")
        raise
    finally:
        session.close()


def can_perform_tavily_search() -> tuple[bool, str]:
    """
    Check if a Tavily search is allowed under daily/weekly/monthly limits.
    Returns:
        (allowed: bool, reason: str) - if not allowed, reason describes which limit was hit.
    """
    daily, weekly, monthly = get_tavily_usage()
    if monthly >= TAVILY_MONTHLY_LIMIT:
        return (False, f"Tavily monthly limit reached ({monthly}/{TAVILY_MONTHLY_LIMIT})")
    if weekly >= TAVILY_WEEKLY_LIMIT:
        return (False, f"Tavily weekly limit reached ({weekly}/{TAVILY_WEEKLY_LIMIT})")
    if daily >= TAVILY_DAILY_LIMIT:
        return (False, f"Tavily daily limit reached ({daily}/{TAVILY_DAILY_LIMIT})")
    return (True, "")
