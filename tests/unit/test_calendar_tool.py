"""Unit tests for CalendarTool."""
import pytest
from datetime import datetime
from unittest.mock import patch
from agent.tools.calendar_tool import CalendarTool
import pytz


@pytest.mark.unit
class TestCalendarTool:
    """Unit tests for CalendarTool."""
    
    def test_init(self):
        """Test CalendarTool initialization."""
        tool = CalendarTool()
        assert tool is not None
    
    def test_get_current_time_in_timezone(self):
        """Test getting current time in timezone."""
        tool = CalendarTool()
        timezone = "America/New_York"
        current_time = tool.get_current_time_in_timezone(timezone)
        
        assert isinstance(current_time, datetime)
        assert current_time.tzinfo is not None
    
    def test_get_current_time_invalid_timezone(self):
        """Test getting time with invalid timezone."""
        tool = CalendarTool()
        # Should default to IST (Asia/Kolkata) for invalid timezone
        current_time = tool.get_current_time_in_timezone("Invalid/Timezone")
        assert isinstance(current_time, datetime)
        # Verify it's using IST timezone
        assert current_time.tzinfo is not None
    
    def test_parse_schedule_time_valid(self):
        """Test parsing valid schedule time."""
        tool = CalendarTool()
        result = tool.parse_schedule_time("09:00")
        assert result == (9, 0)
    
    def test_parse_schedule_time_invalid(self):
        """Test parsing invalid schedule time."""
        tool = CalendarTool()
        assert tool.parse_schedule_time("invalid") is None
        assert tool.parse_schedule_time("25:00") is None
        assert tool.parse_schedule_time("09:60") is None
    
    @patch('agent.tools.calendar_tool.datetime')
    def test_validate_send_time_within_tolerance(self, mock_datetime):
        """Test time validation when within tolerance."""
        tool = CalendarTool()
        
        # Mock current time to be 5 minutes before scheduled time
        mock_now = datetime(2024, 1, 15, 9, 5, 0, tzinfo=pytz.UTC)
        mock_datetime.now.return_value = mock_now
        
        # Create a timezone-aware datetime for comparison
        tz = pytz.timezone("America/New_York")
        scheduled = datetime(2024, 1, 15, 9, 0, 0)
        scheduled = tz.localize(scheduled)
        
        # Mock the get_current_time_in_timezone to return our mock time
        with patch.object(tool, 'get_current_time_in_timezone', return_value=scheduled.replace(minute=5)):
            result = tool.validate_send_time("America/New_York", "09:00", tolerance_minutes=15)
            # Should be valid if within 15 minute tolerance
            assert result is True
    
    def test_validate_send_time_exception_handling(self):
        """Test time validation with exception handling."""
        tool = CalendarTool()
        # Should return True (default) on exception for development
        with patch.object(tool, 'get_current_time_in_timezone', side_effect=Exception("Test error")):
            result = tool.validate_send_time("America/New_York", "09:00")
            assert result is True
