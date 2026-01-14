"""Groq LLM tool for query analysis, summarization, and email generation."""
import time
import logging
from typing import List, Dict, Any
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from config import config

logger = logging.getLogger(__name__)


class GroqTool:
    """Tool for LLM operations using Groq API."""
    
    def __init__(self):
        """Initialize Groq LLM client."""
        if not config.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY not configured")
        self.llm = ChatGroq(
            model=config.GROQ_MODEL,
            groq_api_key=config.GROQ_API_KEY,
            temperature=0.7,
        )
        self.max_retries = 3
        self.base_delay = 1
    
    def _call_llm_with_retry(self, messages: List, system_prompt: str = None) -> str:
        """Call LLM with retry logic."""
        all_messages = []
        if system_prompt:
            all_messages.append(SystemMessage(content=system_prompt))
        all_messages.extend(messages)
        
        for attempt in range(self.max_retries):
            try:
                response = self.llm.invoke(all_messages)
                return response.content
            except Exception as e:
                logger.warning(f"Groq LLM call attempt {attempt + 1} failed: {str(e)}")
                if attempt < self.max_retries - 1:
                    delay = self.base_delay * (2 ** attempt)
                    time.sleep(delay)
                else:
                    logger.error(f"Groq LLM call failed after {self.max_retries} attempts")
                    raise
        
        return ""
    
    def analyze_preferences(self, preferences: Dict[str, Any]) -> List[str]:
        """
        Analyze user preferences and generate search queries.
        
        Args:
            preferences: User preferences dict with topics, timezone, etc.
            
        Returns:
            List of search query strings
        """
        topics = preferences.get("topics", [])
        if not topics:
            return []
        
        system_prompt = """You are a news search query generator. 
        Given user topics of interest, generate 1-2 concise, effective search queries 
        that will find relevant recent news articles. Return only the queries, one per line."""
        
        topics_str = ", ".join(topics)
        user_message = f"User topics: {topics_str}\n\nGenerate search queries:"
        
        try:
            response = self._call_llm_with_retry(
                [HumanMessage(content=user_message)],
                system_prompt
            )
            
            # Parse response into list of queries
            queries = [q.strip() for q in response.split("\n") if q.strip()]
            # Limit to 2 queries max
            queries = queries[:2]
            
            logger.info(f"Generated {len(queries)} search queries from preferences")
            return queries
            
        except Exception as e:
            logger.error(f"Failed to analyze preferences: {str(e)}")
            # Fallback: create simple queries from topics
            return [f"{topic} news" for topic in topics[:2]]
    
    def summarize_article(
        self, 
        article: Dict[str, Any], 
        user_context: Dict[str, Any] = None
    ) -> str:
        """
        Generate a 1-2 line summary of an article.
        
        Args:
            article: Article dict with title, content, url
            user_context: Optional user context for personalization
            
        Returns:
            Summary string (1-2 lines)
        """
        system_prompt = """You are a news summarizer. Generate concise, engaging 
        1-2 line summaries of news articles in TLDR style. Focus on key facts and 
        why it matters. Be unique - avoid repetition."""
        
        title = article.get("title", "")
        content = article.get("content", "")[:500]  # Limit content length
        
        user_message = f"Article Title: {title}\n\nContent: {content}\n\nGenerate a 1-2 line summary:"
        
        try:
            summary = self._call_llm_with_retry(
                [HumanMessage(content=user_message)],
                system_prompt
            )
            
            # Clean up summary (remove quotes, extra whitespace)
            summary = summary.strip().strip('"').strip("'")
            
            logger.info(f"Generated summary for article: {title[:50]}...")
            return summary
            
        except Exception as e:
            logger.error(f"Failed to summarize article: {str(e)}")
            # Fallback: use title as summary
            return title
    
    def generate_email_content(
        self, 
        summaries: List[Dict[str, Any]], 
        user_preferences: Dict[str, Any]
    ) -> str:
        """
        Generate HTML email content from summaries.
        
        Args:
            summaries: List of dicts with article info and summaries
            user_preferences: User preferences for personalization
            
        Returns:
            HTML email content string
        """
        if not summaries:
            return "<p>No new articles found today.</p>"
        
        system_prompt = """You are an email content generator. Create a clean, 
        professional HTML email with article summaries. Use simple HTML tags like 
        <h2>, <p>, <a>, <ul>, <li>. Make it readable and engaging."""
        
        summaries_text = ""
        for i, item in enumerate(summaries, 1):
            title = item.get("title", "")
            summary = item.get("summary", "")
            url = item.get("url", "")
            summaries_text += f"{i}. {title}\n   {summary}\n   URL: {url}\n\n"
        
        user_message = f"""Create an HTML email with these article summaries:
        
{summaries_text}

Include a greeting and closing. Format as clean HTML."""
        
        try:
            html_content = self._call_llm_with_retry(
                [HumanMessage(content=user_message)],
                system_prompt
            )
            
            # Ensure it's valid HTML
            if not html_content.strip().startswith("<"):
                html_content = f"<html><body>{html_content}</body></html>"
            
            logger.info(f"Generated email content with {len(summaries)} articles")
            return html_content
            
        except Exception as e:
            logger.error(f"Failed to generate email content: {str(e)}")
            # Fallback: simple HTML
            html = "<html><body><h2>Your Daily Briefing</h2><ul>"
            for item in summaries:
                title = item.get("title", "")
                summary = item.get("summary", "")
                url = item.get("url", "")
                html += f'<li><strong>{title}</strong><br>{summary}<br><a href="{url}">Read more</a></li>'
            html += "</ul></body></html>"
            return html
