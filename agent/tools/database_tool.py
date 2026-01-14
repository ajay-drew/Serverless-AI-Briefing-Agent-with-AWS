"""Database tool for DynamoDB operations (mock implementation for Day 1-2)."""
import hashlib
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from config import config

logger = logging.getLogger(__name__)


class DatabaseTool:
    """Tool for database operations (mock for Day 1-2, real DynamoDB in Day 3)."""
    
    def __init__(self):
        """Initialize database tool with in-memory storage for Day 1-2."""
        # In-memory storage (will be replaced with DynamoDB in Day 3)
        self.article_hashes: Dict[str, datetime] = {}  # hash -> timestamp
        self.user_history: Dict[str, set] = {}  # user_email -> set of article_ids
        
        logger.info("DatabaseTool initialized with in-memory storage (mock)")
    
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
        exists = hash in self.article_hashes
        logger.debug(f"Article hash check: {hash[:16]}... exists={exists}")
        return exists
    
    def check_user_history(self, user_email: str, article_id: str) -> bool:
        """
        Check if user has already received this article (user-level deduplication).
        
        Args:
            user_email: User email address
            article_id: Article identifier (hash or URL)
            
        Returns:
            True if user has already received this article, False otherwise
        """
        if user_email not in self.user_history:
            return False
        
        exists = article_id in self.user_history[user_email]
        logger.debug(f"User history check: {user_email} - {article_id[:16]}... exists={exists}")
        return exists
    
    def store_article(self, article: Dict[str, Any], hash: str) -> None:
        """
        Store article hash in database.
        
        Args:
            article: Article dictionary
            hash: Article hash string
        """
        self.article_hashes[hash] = datetime.utcnow()
        logger.info(f"Stored article hash: {hash[:16]}...")
    
    def mark_sent_to_user(self, user_email: str, article_id: str) -> None:
        """
        Mark article as sent to user.
        
        Args:
            user_email: User email address
            article_id: Article identifier
        """
        if user_email not in self.user_history:
            self.user_history[user_email] = set()
        
        self.user_history[user_email].add(article_id)
        logger.info(f"Marked article {article_id[:16]}... as sent to {user_email}")
    
    def get_article_hash(self, article: Dict[str, Any]) -> str:
        """
        Generate and return article hash.
        
        Args:
            article: Article dictionary
            
        Returns:
            Article hash string
        """
        return self._generate_article_hash(article)
