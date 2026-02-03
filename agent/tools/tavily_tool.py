"""Tavily search tool for news article retrieval with daily/weekly/monthly rate limits."""
import time
import logging
from typing import List, Dict, Any
from tavily import TavilyClient
from config import config

logger = logging.getLogger(__name__)


def _check_and_record_usage():
    """Import here to avoid circular imports and optional DB dependency at agent import time."""
    try:
        from tavily_usage import can_perform_tavily_search, record_tavily_usage
        allowed, reason = can_perform_tavily_search()
        if not allowed:
            return False, reason, None
        return True, None, record_tavily_usage
    except Exception as e:
        logger.warning(f"Tavily usage check failed (proceeding without limit): {e}")
        return True, None, None


class TavilyTool:
    """Tool for searching news articles using Tavily API with DB-backed rate limits."""

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
        Respects daily (35), weekly (245), and monthly (994) limits stored in DB.

        Args:
            query: Search query string
            max_results: Maximum number of results to return

        Returns:
            List of article dictionaries with title, url, content, published_date, score
        """
        allowed, reason, record_fn = _check_and_record_usage()
        if not allowed:
            logger.warning(f"Tavily search skipped: {reason}")
            return []

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

                if record_fn:
                    try:
                        record_fn()
                    except Exception as e:
                        logger.error(f"Failed to record Tavily usage: {e}")

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
