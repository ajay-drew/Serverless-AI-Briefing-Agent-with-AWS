"""Unit tests for APScheduler functionality."""
import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime
import pytz


@pytest.mark.unit
class TestScheduler:
    """Unit tests for scheduler module."""
    
    @pytest.fixture
    def mock_scheduler(self):
        """Mock APScheduler instance."""
        scheduler = MagicMock()
        scheduler.running = False
        scheduler.get_job = MagicMock(return_value=None)
        scheduler.add_job = MagicMock()
        scheduler.remove_job = MagicMock()
        scheduler.start = MagicMock()
        scheduler.shutdown = MagicMock()
        return scheduler
    
    def test_schedule_user_briefing_success(self, mock_scheduler):
        """Test scheduling a user briefing."""
        with patch('app.scheduler.scheduler', mock_scheduler):
            from app.scheduler import schedule_user_briefing
            
            result = schedule_user_briefing(
                "test@example.com",
                "America/New_York",
                "09:00"
            )
            
            assert result is True
            mock_scheduler.add_job.assert_called_once()
    
    def test_schedule_user_briefing_replaces_existing(self, mock_scheduler):
        """Test scheduling replaces existing job."""
        with patch('app.scheduler.scheduler', mock_scheduler):
            from app.scheduler import schedule_user_briefing
            
            # First call
            schedule_user_briefing("test@example.com", "UTC", "09:00")
            
            # Mock existing job
            mock_scheduler.get_job.return_value = Mock()
            
            # Second call should remove old job
            schedule_user_briefing("test@example.com", "UTC", "10:00")
            
            mock_scheduler.remove_job.assert_called_once()
            assert mock_scheduler.add_job.call_count == 2
    
    def test_schedule_user_briefing_invalid_time(self, mock_scheduler):
        """Test scheduling with invalid time format."""
        with patch('app.scheduler.scheduler', mock_scheduler):
            from app.scheduler import schedule_user_briefing
            
            result = schedule_user_briefing(
                "test@example.com",
                "UTC",
                "invalid:time"
            )
            
            assert result is False
            mock_scheduler.add_job.assert_not_called()
    
    def test_unschedule_user_briefing_success(self, mock_scheduler):
        """Test unscheduling a user briefing."""
        with patch('app.scheduler.scheduler', mock_scheduler):
            from app.scheduler import unschedule_user_briefing
            
            # Mock existing job
            mock_scheduler.get_job.return_value = Mock()
            
            result = unschedule_user_briefing("test@example.com")
            
            assert result is True
            mock_scheduler.remove_job.assert_called_once_with("briefing_test@example.com")
    
    def test_unschedule_user_briefing_not_found(self, mock_scheduler):
        """Test unscheduling non-existent job."""
        with patch('app.scheduler.scheduler', mock_scheduler):
            from app.scheduler import unschedule_user_briefing
            
            mock_scheduler.get_job.return_value = None
            
            result = unschedule_user_briefing("nonexistent@example.com")
            
            assert result is False
            mock_scheduler.remove_job.assert_not_called()
    
    def test_start_scheduler(self, mock_scheduler):
        """Test starting the scheduler."""
        with patch('app.scheduler.scheduler', mock_scheduler), \
             patch('app.scheduler.load_all_scheduled_briefings'):
            from app.scheduler import start_scheduler
            
            start_scheduler()
            
            mock_scheduler.start.assert_called_once()
    
    def test_start_scheduler_already_running(self, mock_scheduler):
        """Test starting scheduler that's already running."""
        with patch('app.scheduler.scheduler', mock_scheduler):
            from app.scheduler import start_scheduler
            
            mock_scheduler.running = True
            start_scheduler()
            
            mock_scheduler.start.assert_not_called()
    
    def test_shutdown_scheduler(self, mock_scheduler):
        """Test shutting down the scheduler."""
        with patch('app.scheduler.scheduler', mock_scheduler):
            from app.scheduler import shutdown_scheduler
            
            mock_scheduler.running = True
            shutdown_scheduler()
            
            mock_scheduler.shutdown.assert_called_once_with(wait=True)
    
    def test_get_scheduled_jobs(self, mock_scheduler):
        """Test getting list of scheduled jobs."""
        with patch('app.scheduler.scheduler', mock_scheduler):
            from app.scheduler import get_scheduled_jobs
            
            mock_job1 = Mock()
            mock_job1.id = "briefing_user1@example.com"
            mock_job1.name = "Daily briefing for user1@example.com"
            mock_job1.next_run_time = datetime.now(pytz.utc)
            mock_job1.trigger = "cron"
            
            mock_scheduler.get_jobs.return_value = [mock_job1]
            
            jobs = get_scheduled_jobs()
            
            assert len(jobs) == 1
            assert jobs[0]["id"] == "briefing_user1@example.com"
            assert "next_run_time" in jobs[0]
    
    def test_send_briefing_success(self, mock_scheduler):
        """Test send_briefing function."""
        with patch('app.scheduler.agent_runner.run_scheduled_briefing') as mock_run:
            from app.scheduler import send_briefing
            
            mock_run.return_value = {
                "success": True,
                "articles_sent": 5
            }
            
            send_briefing("test@example.com")
            
            mock_run.assert_called_once_with("test@example.com")
    
    def test_send_briefing_failure(self, mock_scheduler):
        """Test send_briefing when it fails."""
        with patch('app.scheduler.agent_runner.run_scheduled_briefing') as mock_run:
            from app.scheduler import send_briefing
            
            mock_run.return_value = {
                "success": False,
                "error": "Test error"
            }
            
            # Should not raise exception
            send_briefing("test@example.com")
            
            mock_run.assert_called_once()
    
    def test_load_all_scheduled_briefings(self, mock_scheduler):
        """Test loading all scheduled briefings from database."""
        with patch('app.scheduler.scheduler', mock_scheduler), \
             patch('app.scheduler.db_manager.get_session') as mock_get_session, \
             patch('app.scheduler.schedule_user_briefing') as mock_schedule:
            
            from app.scheduler import load_all_scheduled_briefings
            
            # Mock database session
            mock_session = MagicMock()
            mock_get_session.return_value = mock_session
            
            # Mock users
            mock_user1 = Mock()
            mock_user1.email = "user1@example.com"
            mock_user1.timezone = "UTC"
            mock_user1.briefing_time = "09:00"
            
            mock_user2 = Mock()
            mock_user2.email = "user2@example.com"
            mock_user2.timezone = "America/New_York"
            mock_user2.briefing_time = "08:00"
            
            mock_session.query().all.return_value = [mock_user1, mock_user2]
            mock_schedule.return_value = True
            
            load_all_scheduled_briefings()
            
            assert mock_schedule.call_count == 2
