"""Unit tests for EmailTool."""
import pytest
import logging
from unittest.mock import patch, MagicMock, mock_open
from agent.tools.email_tool import EmailTool


@pytest.mark.unit
class TestEmailTool:
    """Unit tests for EmailTool."""
    
    def test_init_smtp_disabled(self):
        """Test EmailTool initialization with SMTP disabled."""
        with patch('config.config') as mock_config:
            mock_config.SMTP_ENABLED = False
            mock_config.SMTP_FROM_EMAIL = "from@test.com"
            tool = EmailTool()
            assert tool.use_smtp is False
    
    def test_init_smtp_enabled(self):
        """Test EmailTool initialization with SMTP enabled."""
        with patch('config.config') as mock_config:
            mock_config.SMTP_ENABLED = True
            mock_config.SMTP_USERNAME = "user@test.com"
            mock_config.SMTP_PASSWORD = "password"
            mock_config.SMTP_FROM_EMAIL = "from@test.com"
            mock_config.SMTP_SERVER = "smtp.test.com"
            mock_config.SMTP_PORT = 587
            tool = EmailTool()
            assert tool.use_smtp is True
    
    def test_send_email_mock_mode(self, caplog):
        """Test sending email in mock mode."""
        with patch('config.config') as mock_config, \
             patch('builtins.open', mock_open()):
            
            mock_config.SMTP_ENABLED = False
            mock_config.SMTP_FROM_EMAIL = "from@test.com"
            
            # Set logging level to capture INFO logs
            with caplog.at_level(logging.INFO, logger='agent.tools.email_tool'):
                tool = EmailTool()
                result = tool.send_email(
                    to="recipient@example.com",
                    subject="Test Subject",
                    html_content="<html><body>Test content</body></html>"
                )
                
                assert result["status"] == "saved"
                assert result["to"] == "recipient@example.com"
                assert result["subject"] == "Test Subject"
                assert "message_id" in result
                assert "mock-" in result["message_id"]
                assert result["method"] == "mock"
                
                # Check that email was logged
                assert "EMAIL (MOCK MODE" in caplog.text
    
    def test_send_email_empty_content(self):
        """Test sending email with empty content."""
        with patch('config.config') as mock_config, \
             patch('builtins.open', mock_open()):
            
            mock_config.SMTP_ENABLED = False
            mock_config.SMTP_FROM_EMAIL = "from@test.com"
            
            tool = EmailTool()
            result = tool.send_email(
                to="recipient@example.com",
                subject="Test",
                html_content=""
            )
            
            assert result["status"] == "saved"
            assert result["message_id"] is not None
            assert result["method"] == "mock"
    
    def test_draft_email(self):
        """Test drafting an email."""
        with patch('config.config') as mock_config:
            mock_config.SMTP_ENABLED = False
            mock_config.SMTP_FROM_EMAIL = "from@test.com"
            
            tool = EmailTool()
            draft = tool.draft_email(
                to="recipient@example.com",
                subject="Test",
                html_content="<html><body>Test</body></html>"
            )
            
            assert draft["to"] == "recipient@example.com"
            assert draft["subject"] == "Test"
            assert "html_content" in draft
            assert "text_content" in draft
