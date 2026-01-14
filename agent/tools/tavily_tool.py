"""Tavily search tool for news article retrieval."""
import time
import logging
from typing import List, Dict, Any
from tavily import TavilyClient
from config import config

logger = logging.getLogger(__name__)


class TavilyTool:
    """Tool for searching news articles using Tavily API."""
    
    def __init__(self):
        """Initialize Tavily client."""
        if not config.TAVILY_API_KEY:
            raise ValueError("TAVILY_API_KEY not configured")
        self.client = TavilyClient(api_key=config.TAVILY_API_KEY)
        self.max_retries = 3
        self.base_delay = 1
    
    def search_news(
        self, 
        query: str, 
        max_results: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search for news articles using Tavily API.
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return
            
        Returns:
            List of article dictionaries with title, url, content, published_date, score
        """
        for attempt in range(self.max_retries):
            try:
                response = self.client.search(
                    query=query,
                    max_results=max_results,
                    search_depth="advanced",
                    include_answer=False,
                    include_raw_content=True
                )
                
                articles = []
                for result in response.get("results", []):
                    article = {
                        "title": result.get("title", ""),
                        "url": result.get("url", ""),
                        "content": result.get("content", ""),
                        "published_date": result.get("published_date"),
                        "score": result.get("score", 0.0),
                        "raw_content": result.get("raw_content", ""),
                    }
                    articles.append(article)
                
                logger.info(f"Tavily search successful: {len(articles)} articles for query '{query}'")
                return articles
                
            except Exception as e:
                logger.warning(f"Tavily search attempt {attempt + 1} failed: {str(e)}")
                if attempt < self.max_retries - 1:
                    delay = self.base_delay * (2 ** attempt)  # Exponential backoff
                    time.sleep(delay)
                else:
                    logger.error(f"Tavily search failed after {self.max_retries} attempts")
                    raise
        
        return []
