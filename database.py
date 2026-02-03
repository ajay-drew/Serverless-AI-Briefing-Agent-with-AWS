"""Database models and connection management using SQLAlchemy."""
import os
import logging
from datetime import datetime
from typing import Optional
from sqlalchemy import create_engine, Column, String, DateTime, JSON, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
from sqlalchemy.pool import StaticPool
from config import config

logger = logging.getLogger(__name__)

Base = declarative_base()


class User(Base):
    """User table for storing user preferences and settings."""
    __tablename__ = "users"
    
    email = Column(String(255), primary_key=True)
    preferences = Column(JSON, nullable=False)  # {"topics": ["AI", "tech"]}
    timezone = Column(String(50), nullable=False, default="UTC")
    briefing_time = Column(String(10), nullable=False, default="09:00")  # HH:MM format
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    user_articles = relationship("UserArticle", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(email='{self.email}', timezone='{self.timezone}', briefing_time='{self.briefing_time}')>"


class Article(Base):
    """Article table for storing news articles and deduplication."""
    __tablename__ = "articles"
    
    id = Column(String(64), primary_key=True)  # SHA256 hash of title+url
    url_hash = Column(String(64), unique=True, nullable=False, index=True)  # For quick lookup
    title = Column(Text, nullable=False)
    url = Column(Text, nullable=False)
    summary = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    user_articles = relationship("UserArticle", back_populates="article", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Article(id='{self.id[:16]}...', title='{self.title[:50]}...')>"


class UserArticle(Base):
    """Junction table tracking which articles were sent to which users."""
    __tablename__ = "user_articles"
    
    user_email = Column(String(255), ForeignKey("users.email"), primary_key=True)
    article_id = Column(String(64), ForeignKey("articles.id"), primary_key=True)
    sent_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="user_articles")
    article = relationship("Article", back_populates="user_articles")
    
    def __repr__(self):
        return f"<UserArticle(user='{self.user_email}', article='{self.article_id[:16]}...', sent_at='{self.sent_at}')>"


class DatabaseManager:
    """Database connection and session management."""
    
    def __init__(self, database_url: Optional[str] = None):
        """
        Initialize database manager with connection.
        
        Args:
            database_url: PostgreSQL connection URL. If None, uses in-memory SQLite for testing.
        """
        self.database_url = database_url or config.DATABASE_URL
        
        # Use in-memory SQLite if no DATABASE_URL provided (for testing)
        if not self.database_url or self.database_url.startswith("sqlite"):
            if not self.database_url:
                logger.warning("No DATABASE_URL provided, using in-memory SQLite for testing")
                self.database_url = "sqlite:///:memory:"
            self.engine = create_engine(
                self.database_url,
                connect_args={"check_same_thread": False},
                poolclass=StaticPool,
                echo=False
            )
        else:
            # PostgreSQL connection (optimized for Neon serverless)
            connect_args = {}
            
            # Clean up Neon URL - remove unsupported parameters
            clean_url = self.database_url
            if "neon.tech" in self.database_url:
                # Remove channel_binding parameter (not supported by SQLAlchemy)
                clean_url = clean_url.replace("&channel_binding=require", "")
                clean_url = clean_url.replace("channel_binding=require&", "")
                clean_url = clean_url.replace("?channel_binding=require", "")
                logger.info("Detected Neon database - cleaned URL and using SSL mode")
            
            self.engine = create_engine(
                clean_url,
                pool_pre_ping=True,  # Verify connections before using (important for Neon)
                pool_size=5,  # Neon handles scaling, so modest pool is fine
                max_overflow=10,
                pool_recycle=300,  # Recycle connections after 5 minutes (Neon best practice)
                connect_args=connect_args,
                echo=False
            )
        
        # Create session factory
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
        logger.info(f"DatabaseManager initialized with: {self._mask_url(self.database_url)}")
    
    def _mask_url(self, url: str) -> str:
        """Mask password in database URL for logging."""
        if "://" in url and "@" in url:
            parts = url.split("://")
            if len(parts) == 2:
                credentials_and_host = parts[1]
                if "@" in credentials_and_host:
                    creds, host = credentials_and_host.split("@", 1)
                    if ":" in creds:
                        user = creds.split(":")[0]
                        return f"{parts[0]}://{user}:****@{host}"
        return url
    
    def create_tables(self):
        """Create all tables in the database."""
        Base.metadata.create_all(bind=self.engine)
        logger.info("Database tables created successfully")
    
    def drop_tables(self):
        """Drop all tables in the database (for testing)."""
        Base.metadata.drop_all(bind=self.engine)
        logger.info("Database tables dropped")
    
    def get_session(self) -> Session:
        """
        Get a new database session.
        
        Returns:
            SQLAlchemy Session object
        """
        return self.SessionLocal()
    
    def health_check(self) -> bool:
        """
        Check if database connection is healthy.
        
        Returns:
            True if connection is healthy, False otherwise
        """
        try:
            session = self.get_session()
            session.execute("SELECT 1")
            session.close()
            return True
        except Exception as e:
            logger.error(f"Database health check failed: {str(e)}")
            return False


# Global database manager instance
db_manager = DatabaseManager()


def get_db() -> Session:
    """
    Dependency function for FastAPI to get database session.
    
    Yields:
        SQLAlchemy Session object
    """
    db = db_manager.get_session()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database tables."""
    db_manager.create_tables()
    logger.info("Database initialized")


if __name__ == "__main__":
    # Test database connection
    logging.basicConfig(level=logging.INFO)
    
    print("Testing database connection...")
    init_db()
    
    if db_manager.health_check():
        print("✓ Database connection healthy")
    else:
        print("✗ Database connection failed")
    
    # Test creating a user
    session = db_manager.get_session()
    try:
        test_user = User(
            email="test@example.com",
            preferences={"topics": ["AI", "technology"]},
            timezone="America/New_York",
            briefing_time="09:00"
        )
        session.add(test_user)
        session.commit()
        print(f"✓ Created test user: {test_user}")
        
        # Query it back
        user = session.query(User).filter(User.email == "test@example.com").first()
        print(f"✓ Retrieved user: {user}")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        session.rollback()
    finally:
        session.close()
