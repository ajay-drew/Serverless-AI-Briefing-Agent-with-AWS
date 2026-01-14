"""Configuration module for loading environment variables."""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Application configuration from environment variables."""
    
    # Groq API
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-70b-versatile")
    
    # Tavily API
    TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "")
    
    # AWS Configuration
    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", "")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "")
    AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
    
    # SES Configuration
    SES_FROM_EMAIL = os.getenv("SES_FROM_EMAIL", "")
    TEST_EMAIL_RECIPIENT = os.getenv("TEST_EMAIL_RECIPIENT", "")
    
    # SMTP Configuration (for sending emails without AWS SES)
    SMTP_ENABLED = os.getenv("SMTP_ENABLED", "false").lower() == "true"
    SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
    
    # DynamoDB Table Names
    DYNAMODB_NEWS_ARTICLES_TABLE = os.getenv("DYNAMODB_NEWS_ARTICLES_TABLE", "news_articles")
    DYNAMODB_USER_SUMMARIES_TABLE = os.getenv("DYNAMODB_USER_SUMMARIES_TABLE", "user_summaries")
    DYNAMODB_USER_PREFERENCES_TABLE = os.getenv("DYNAMODB_USER_PREFERENCES_TABLE", "user_preferences")
    
    @classmethod
    def validate(cls) -> bool:
        """Validate that required configuration is present."""
        required = [
            cls.GROQ_API_KEY,
            cls.TAVILY_API_KEY,
        ]
        return all(required)


# Global config instance
config = Config()
