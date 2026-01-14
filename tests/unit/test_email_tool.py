"""Unit tests for EmailTool."""
import pytest
import logging
from unittest.mock import patch, MagicMock
from agent.tools.email_tool import EmailTool


@pytest.mark.unit
class TestEmailTool:
    """Unit tests for EmailTool."""
    
    def test_init(self, mock_config):
        """Test EmailTool initialization."""
        tool = EmailTool()
        assert tool.from_email == "test@example.com"
    
    def test_send_email_mock_mode(self, mock_config, caplog):
        """Test sending email in mock mode (Day 1-2)."""
        # Set logging level to capture INFO logs
        with caplog.at_level(logging.INFO, logger='agent.tools.email_tool'):
            tool = EmailTool()
            result = tool.send_email(
                to="recipient@example.com",
                subject="Test Subject",
                html_content="<html><body>Test content</body></html>"
            )
            
            assert result["status"] == "logged"
            assert result["to"] == "recipient@example.com"
            assert result["subject"] == "Test Subject"
            assert "message_id" in result
            assert "mock-" in result["message_id"]
            
            # Check that email was logged
            assert "EMAIL (MOCK MODE" in caplog.text
    
    def test_send_email_empty_content(self, mock_config):
        """Test sending email with empty content."""
        tool = EmailTool()
        result = tool.send_email(
            to="recipient@example.com",
            subject="Test",
            html_content=""
        )
        
        assert result["status"] == "logged"
        assert result["message_id"] is not None
