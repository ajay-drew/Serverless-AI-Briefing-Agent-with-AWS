"""Database tool for PostgreSQL operations."""
import hashlib
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from database import db_manager, User, Article, UserArticle

logger = logging.getLogger(__name__)


class DatabaseTool:
    """Tool for database operations using PostgreSQL."""
    
    def __init__(self, session=None):
        """
        Initialize database tool with PostgreSQL connection.
        
        Args:
            session: Optional SQLAlchemy session. If None, creates new sessions per operation.
        """
        self.session = session
        self.use_external_session = session is not None
        logger.info("DatabaseTool initialized with PostgreSQL")
    
    def _get_session(self):
        """Get database session (either provided or create new)."""
        if self.use_external_session:
            return self.session
        return db_manager.get_session()
    
    def _close_session(self, session):
        """Close session only if it was created internally."""
        if not self.use_external_session:
            session.close()
    
    def _generate_article_hash(self, article: Dict[str, Any]) -> str:
        """Generate hash for article deduplication."""
        # Use title + url for hash
        content = f"{article.get('title', '')}{article.get('url', '')}"
        return hashlib.sha256(content.encode()).hexdigest()
    
    def check_article_hash(self, hash: str) -> bool:
        """
        Check if article hash exists (article-level deduplication).
        
        Args:
            hash: Article hash string
            
        Returns:
            True if article exists, False otherwise
        """
        session = self._get_session()
        try:
            article = session.query(Article).filter(Article.url_hash == hash).first()
            exists = article is not None
            logger.debug(f"Article hash check: {hash[:16]}... exists={exists}")
            return exists
        except Exception as e:
            logger.error(f"Error checking article hash: {str(e)}")
            return False
        finally:
            self._close_session(session)
    
    def check_user_history(self, user_email: str, article_id: str) -> bool:
        """
        Check if user has already received this article (user-level deduplication).
        
        Args:
            user_email: User email address
            article_id: Article identifier (hash or URL)
            
        Returns:
            True if user has already received this article, False otherwise
        """
        session = self._get_session()
        try:
            user_article = session.query(UserArticle).filter(
                UserArticle.user_email == user_email,
                UserArticle.article_id == article_id
            ).first()
            exists = user_article is not None
            logger.debug(f"User history check: {user_email} - {article_id[:16]}... exists={exists}")
            return exists
        except Exception as e:
            logger.error(f"Error checking user history: {str(e)}")
            return False
        finally:
            self._close_session(session)
    
    def store_article(self, article: Dict[str, Any], hash: str) -> None:
        """
        Store article in database (upsert on conflict).
        
        Args:
            article: Article dictionary
            hash: Article hash string
        """
        session = self._get_session()
        try:
            # Check if article already exists
            existing = session.query(Article).filter(Article.url_hash == hash).first()
            
            if not existing:
                # Create new article
                new_article = Article(
                    id=hash,
                    url_hash=hash,
                    title=article.get('title', ''),
                    url=article.get('url', ''),
                    summary=article.get('summary', ''),
                    created_at=datetime.utcnow()
                )
                session.add(new_article)
                session.commit()
                logger.info(f"Stored new article: {hash[:16]}...")
            else:
                logger.debug(f"Article already exists: {hash[:16]}...")
        except IntegrityError:
            session.rollback()
            logger.debug(f"Article already exists (integrity error): {hash[:16]}...")
        except Exception as e:
            session.rollback()
            logger.error(f"Error storing article: {str(e)}")
        finally:
            self._close_session(session)
    
    def mark_sent_to_user(self, user_email: str, article_id: str) -> None:
        """
        Mark article as sent to user.
        
        Args:
            user_email: User email address
            article_id: Article identifier
        """
        session = self._get_session()
        try:
            # Check if already marked
            existing = session.query(UserArticle).filter(
                UserArticle.user_email == user_email,
                UserArticle.article_id == article_id
            ).first()
            
            if not existing:
                user_article = UserArticle(
                    user_email=user_email,
                    article_id=article_id,
                    sent_at=datetime.utcnow()
                )
                session.add(user_article)
                session.commit()
                logger.info(f"Marked article {article_id[:16]}... as sent to {user_email}")
            else:
                logger.debug(f"Article already marked as sent: {article_id[:16]}...")
        except IntegrityError:
            session.rollback()
            logger.debug(f"User-article relationship already exists")
        except Exception as e:
            session.rollback()
            logger.error(f"Error marking article as sent: {str(e)}")
        finally:
            self._close_session(session)
    
    def get_article_hash(self, article: Dict[str, Any]) -> str:
        """
        Generate and return article hash.
        
        Args:
            article: Article dictionary
            
        Returns:
            Article hash string
        """
        return self._generate_article_hash(article)
    
    def get_user_preferences(self, user_email: str) -> Optional[Dict[str, Any]]:
        """
        Get user preferences from database.
        
        Args:
            user_email: User email address
            
        Returns:
            User preferences dictionary or None if not found
        """
        session = self._get_session()
        try:
            user = session.query(User).filter(User.email == user_email).first()
            if user:
                return {
                    "topics": user.preferences.get("topics", []),
                    "timezone": user.timezone,
                    "schedule_time": user.briefing_time
                }
            return None
        except Exception as e:
            logger.error(f"Error getting user preferences: {str(e)}")
            return None
        finally:
            self._close_session(session)
    
    def save_user_preferences(
        self,
        user_email: str,
        preferences: Dict[str, Any],
        timezone: str,
        briefing_time: str
    ) -> bool:
        """
        Save or update user preferences.
        
        Args:
            user_email: User email address
            preferences: User preferences dictionary
            timezone: User timezone
            briefing_time: Briefing time in HH:MM format
            
        Returns:
            True if successful, False otherwise
        """
        session = self._get_session()
        try:
            user = session.query(User).filter(User.email == user_email).first()
            
            if user:
                # Update existing user
                user.preferences = preferences
                user.timezone = timezone
                user.briefing_time = briefing_time
            else:
                # Create new user
                user = User(
                    email=user_email,
                    preferences=preferences,
                    timezone=timezone,
                    briefing_time=briefing_time,
                    created_at=datetime.utcnow()
                )
                session.add(user)
            
            session.commit()
            logger.info(f"Saved preferences for user: {user_email}")
            return True
        except Exception as e:
            session.rollback()
            logger.error(f"Error saving user preferences: {str(e)}")
            return False
        finally:
            self._close_session(session)
