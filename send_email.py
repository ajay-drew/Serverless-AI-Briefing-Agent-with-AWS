"""Script to draft and send emails using the EmailTool."""
import logging
import sys
from typing import Optional
from agent.tools.email_tool import EmailTool
from config import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def send_test_email():
    """Send a test email using the EmailTool."""
    logger.info("=" * 80)
    logger.info("Email Sending Tool")
    logger.info("=" * 80)
    
    # Check for recipient email
    recipient = config.TEST_EMAIL_RECIPIENT
    if not recipient:
        logger.error("TEST_EMAIL_RECIPIENT not set in .env file")
        logger.info("Please add TEST_EMAIL_RECIPIENT=your-email@example.com to your .env file")
        return 1
    
    # Check for from email
    from_email = config.SES_FROM_EMAIL
    if not from_email:
        logger.warning("SES_FROM_EMAIL not set in .env file")
        logger.info("Using default: noreply@example.com")
        from_email = "noreply@example.com"
    
    logger.info(f"From: {from_email}")
    logger.info(f"To: {recipient}")
    logger.info("-" * 80)
    
    # Initialize email tool
    email_tool = EmailTool()
    
    # Draft email content
    subject = "Test Email from AI Briefing Agent"
    html_content = """
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
            <h2 style="color: #2c3e50;">AI Briefing Agent - Test Email</h2>
            <p>This is a test email sent from the AI Briefing Agent system.</p>
            <p>The email tool is working correctly and can send emails to your configured address.</p>
            <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
            <p style="color: #7f8c8d; font-size: 12px;">
                This is an automated message from the Serverless AI Briefing Agent with AWS.
            </p>
        </div>
    </body>
    </html>
    """
    
    # Draft the email
    logger.info("Drafting email...")
    draft = email_tool.draft_email(
        to=recipient,
        subject=subject,
        html_content=html_content
    )
    
    logger.info("Email draft created successfully")
    logger.info("-" * 80)
    
    # Send the email
    logger.info("Sending email...")
    result = email_tool.send_email(
        to=recipient,
        subject=subject,
        html_content=html_content
    )
    
    logger.info("=" * 80)
    if result.get("status") == "sent":
        logger.info("✓ Email sent successfully!")
        logger.info(f"Message ID: {result.get('message_id')}")
        logger.info(f"Method: {result.get('method')}")
    else:
        logger.info("✓ Email prepared (mock mode)")
        logger.info(f"Status: {result.get('status')}")
        logger.info(f"Method: {result.get('method')}")
        logger.info("Note: Configure AWS SES credentials in .env to send real emails")
    logger.info("=" * 80)
    
    return 0


def send_custom_email(subject: str, html_content: str, recipient: Optional[str] = None):
    """Send a custom email with provided content."""
    recipient = recipient or config.TEST_EMAIL_RECIPIENT
    if not recipient:
        logger.error("No recipient email specified")
        return 1
    
    email_tool = EmailTool()
    result = email_tool.send_email(
        to=recipient,
        subject=subject,
        html_content=html_content
    )
    
    return 0 if result.get("status") in ["sent", "logged"] else 1


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Custom email mode
        if len(sys.argv) < 4:
            print("Usage: python send_email.py <subject> <html_content> [recipient]")
            sys.exit(1)
        subject = sys.argv[1]
        html_content = sys.argv[2]
        recipient = sys.argv[3] if len(sys.argv) > 3 else None
        exit(send_custom_email(subject, html_content, recipient))
    else:
        # Test email mode
        exit(send_test_email())
