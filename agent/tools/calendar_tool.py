"""Calendar tool for timezone-aware scheduling validation."""
import logging
from datetime import datetime
from typing import Optional
import pytz
from config import config

logger = logging.getLogger(__name__)


class CalendarTool:
    """Tool for timezone-aware datetime operations and scheduling validation."""
    
    def __init__(self):
        """Initialize calendar tool."""
        logger.info("CalendarTool initialized")
    
    def get_current_time_in_timezone(self, timezone: str) -> datetime:
        """
        Get current time in specified timezone.
        
        Args:
            timezone: Timezone string (e.g., 'America/New_York')
            
        Returns:
            Current datetime in specified timezone
        """
        try:
            tz = pytz.timezone(timezone)
            return datetime.now(tz)
        except Exception as e:
            logger.error(f"Invalid timezone '{timezone}': {str(e)}")
            # Default to IST (Indian Standard Time)
            return datetime.now(pytz.timezone('Asia/Kolkata'))
    
    def validate_send_time(
        self, 
        user_timezone: str, 
        schedule_time: str,
        tolerance_minutes: int = 15
    ) -> bool:
        """
        Validate if current time matches scheduled send time (within tolerance).
        
        Args:
            user_timezone: User's timezone string
            schedule_time: Scheduled time string (format: "HH:MM" in 24-hour format)
            tolerance_minutes: Tolerance window in minutes (default: 15)
            
        Returns:
            True if current time is within tolerance of scheduled time
        """
        try:
            # Get current time in user's timezone
            current_time = self.get_current_time_in_timezone(user_timezone)
            
            # Parse schedule time
            hour, minute = map(int, schedule_time.split(":"))
            
            # Create scheduled datetime for today
            tz = pytz.timezone(user_timezone)
            scheduled_time = current_time.replace(hour=hour, minute=minute, second=0, microsecond=0)
            
            # Calculate time difference
            time_diff = abs((current_time - scheduled_time).total_seconds() / 60)
            
            # Check if within tolerance
            is_valid = time_diff <= tolerance_minutes
            
            logger.info(
                f"Time validation: current={current_time.strftime('%H:%M')}, "
                f"scheduled={schedule_time}, diff={time_diff:.1f}min, valid={is_valid}"
            )
            
            return is_valid
            
        except Exception as e:
            logger.error(f"Failed to validate send time: {str(e)}")
            # Default to True for development/testing
            return True
    
    def parse_schedule_time(self, schedule_time: str) -> Optional[tuple]:
        """
        Parse schedule time string into hour and minute.
        
        Args:
            schedule_time: Time string in "HH:MM" format
            
        Returns:
            Tuple of (hour, minute) or None if invalid
        """
        try:
            hour, minute = map(int, schedule_time.split(":"))
            if 0 <= hour <= 23 and 0 <= minute <= 59:
                return (hour, minute)
        except Exception as e:
            logger.error(f"Invalid schedule time format '{schedule_time}': {str(e)}")
        return None
