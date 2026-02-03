"""Email tool for SMTP email sending."""
import logging
from typing import Dict, Any, Optional
import os
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from config import config

logger = logging.getLogger(__name__)


class EmailTool:
    """Tool for sending emails via SMTP or mock mode."""
    
    def __init__(self):
        """Initialize email tool."""
        # Use email from .env file, fallback to default if not set
        self.from_email = config.SMTP_FROM_EMAIL or "noreply@example.com"
        
        # Create temp folder for saving emails in mock mode
        self.temp_email_dir = os.path.join(os.getcwd(), "temp", "emails")
        os.makedirs(self.temp_email_dir, exist_ok=True)
        
        # Log configuration
        if config.SMTP_FROM_EMAIL:
            logger.info(f"EmailTool: Using FROM email: {config.SMTP_FROM_EMAIL}")
        else:
            logger.warning(f"EmailTool: SMTP_FROM_EMAIL not set, using default: {self.from_email}")
        
        # Initialize email sending method priority: SMTP > Mock
        self.use_smtp = False
        
        # Try SMTP
        if config.SMTP_ENABLED:
            if config.SMTP_USERNAME and config.SMTP_PASSWORD:
                self.use_smtp = True
                logger.info(f"EmailTool initialized with SMTP ({config.SMTP_SERVER}:{config.SMTP_PORT})")
            else:
                logger.warning("SMTP_ENABLED is true but SMTP_USERNAME or SMTP_PASSWORD not set")
        
        # Fall back to mock mode
        if not self.use_smtp:
            logger.info(f"EmailTool initialized (mock mode - saving emails to: {self.temp_email_dir})")
            logger.info("   To enable email sending: Configure SMTP in .env")
    
    def send_email(
        self, 
        to: str, 
        subject: str, 
        html_content: str,
        text_content: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send email via SMTP or mock mode.
        
        Args:
            to: Recipient email address
            subject: Email subject line
            html_content: HTML email content
            text_content: Optional plain text content (auto-generated if not provided)
            
        Returns:
            Dictionary with message_id and status
        """
        # Priority: SMTP > Mock
        if self.use_smtp:
            # SMTP sending
            return self._send_email_smtp(to, subject, html_content, text_content)
        else:
            # Mock implementation
            return self._send_email_mock(to, subject, html_content)
    
    def _send_email_smtp(
        self,
        to: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None
    ) -> Dict[str, Any]:
        """Send email via SMTP."""
        try:
            # Generate text content from HTML if not provided
            if not text_content:
                import re
                text_content = re.sub(r'<[^>]+>', '', html_content)
                text_content = text_content.strip()
            
            # Create email message
            msg = MIMEMultipart('alternative')
            msg['From'] = self.from_email
            msg['To'] = to
            msg['Subject'] = subject
            
            # Add both text and HTML parts
            text_part = MIMEText(text_content, 'plain')
            html_part = MIMEText(html_content, 'html')
            msg.attach(text_part)
            msg.attach(html_part)
            
            # Connect to SMTP server and send
            with smtplib.SMTP(config.SMTP_SERVER, config.SMTP_PORT) as server:
                server.starttls()  # Enable encryption
                server.login(config.SMTP_USERNAME, config.SMTP_PASSWORD)
                server.send_message(msg)
            
            logger.info(f"Email sent successfully via SMTP to {to}")
            
            # Also save to temp folder for backup
            self._save_email_to_temp(to, subject, html_content, msg)
            
            return {
                "message_id": f"smtp-{to}-{hash(html_content)}",
                "status": "sent",
                "to": to,
                "subject": subject,
                "method": "smtp"
            }
            
        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"SMTP authentication failed: {str(e)}")
            logger.warning("   Please check your SMTP_USERNAME and SMTP_PASSWORD in .env")
            logger.warning("   For Gmail: Use an App Password, not your regular password")
            return self._send_email_mock(to, subject, html_content)
        except smtplib.SMTPException as e:
            logger.error(f"SMTP error: {str(e)}")
            return self._send_email_mock(to, subject, html_content)
        except Exception as e:
            logger.error(f"Unexpected error sending email via SMTP: {str(e)}")
            return self._send_email_mock(to, subject, html_content)
    
    def _save_email_to_temp(
        self,
        to: str,
        subject: str,
        html_content: str,
        msg: MIMEMultipart
    ) -> None:
        """Helper method to save email to temp folder."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_to = to.replace("@", "_at_").replace(".", "_")
        safe_subject = "".join(c for c in subject if c.isalnum() or c in (' ', '-', '_')).strip()[:50]
        
        # Save as .eml file
        eml_filename = f"email_{timestamp}_{safe_to}_{safe_subject}.eml"
        eml_path = os.path.join(self.temp_email_dir, eml_filename)
        with open(eml_path, 'w', encoding='utf-8') as f:
            f.write(msg.as_string())
        
        # Save as .html file
        html_filename = f"email_{timestamp}_{safe_to}_{safe_subject}.html"
        html_path = os.path.join(self.temp_email_dir, html_filename)
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"Email also saved to: {eml_path}")
    
    def _send_email_mock(
        self, 
        to: str, 
        subject: str, 
        html_content: str
    ) -> Dict[str, Any]:
        """Mock email sending (saves to temp folder as HTML and EML files)."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_to = to.replace("@", "_at_").replace(".", "_")
        safe_subject = "".join(c for c in subject if c.isalnum() or c in (' ', '-', '_')).strip()[:50]
        
        # Create email message using Python's email library
        msg = MIMEMultipart('alternative')
        msg['From'] = self.from_email
        msg['To'] = to
        msg['Subject'] = subject
        msg['Date'] = datetime.now().strftime('%a, %d %b %Y %H:%M:%S %z')
        
        # Add HTML content
        html_part = MIMEText(html_content, 'html')
        msg.attach(html_part)
        
        # Generate text content from HTML
        import re
        text_content = re.sub(r'<[^>]+>', '', html_content)
        text_content = text_content.strip()
        text_part = MIMEText(text_content, 'plain')
        msg.attach(text_part)
        
        # Save as .eml file (standard email format)
        eml_filename = f"email_{timestamp}_{safe_to}_{safe_subject}.eml"
        eml_path = os.path.join(self.temp_email_dir, eml_filename)
        with open(eml_path, 'w', encoding='utf-8') as f:
            f.write(msg.as_string())
        
        # Save as .html file for easy preview
        html_filename = f"email_{timestamp}_{safe_to}_{safe_subject}.html"
        html_path = os.path.join(self.temp_email_dir, html_filename)
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info("=" * 80)
        logger.info("EMAIL (MOCK MODE - Saved to temp folder)")
        logger.info(f"From: {self.from_email}")
        logger.info(f"To: {to}")
        logger.info(f"Subject: {subject}")
        logger.info(f"Content Length: {len(html_content)} characters")
        logger.info(f"Saved EML file: {eml_path}")
        logger.info(f"Saved HTML file: {html_path}")
        logger.info("-" * 80)
        logger.info(f"HTML Preview:\n{html_content[:300]}...")  # First 300 chars
        logger.info("=" * 80)
        
        return {
            "message_id": f"mock-{to}-{hash(html_content)}",
            "status": "saved",
            "to": to,
            "subject": subject,
            "method": "mock",
            "eml_path": eml_path,
            "html_path": html_path
        }
    
    def draft_email(
        self,
        to: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Draft an email (prepare content without sending).
        
        Args:
            to: Recipient email address
            subject: Email subject line
            html_content: HTML email content
            text_content: Optional plain text content
            
        Returns:
            Dictionary with email draft details
        """
        if not text_content:
            import re
            text_content = re.sub(r'<[^>]+>', '', html_content)
            text_content = text_content.strip()
        
        draft = {
            "to": to,
            "from": self.from_email,
            "subject": subject,
            "html_content": html_content,
            "text_content": text_content,
            "html_length": len(html_content),
            "text_length": len(text_content),
        }
        
        logger.info(f"Email draft created for {to}")
        logger.info(f"Subject: {subject}")
        logger.info(f"HTML: {draft['html_length']} chars, Text: {draft['text_length']} chars")
        
        return draft