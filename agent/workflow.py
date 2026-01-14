"""LangGraph workflow definition for the AI briefing agent."""
import logging
from typing import Literal
from langgraph.graph import StateGraph, END
from agent.state import AgentState
from agent.tools import (
    TavilyTool,
    GroqTool,
    DatabaseTool,
    EmailTool,
    CalendarTool,
)

logger = logging.getLogger(__name__)


class BriefingAgentWorkflow:
    """LangGraph workflow for AI briefing agent."""
    
    def __init__(self):
        """Initialize workflow with tools."""
        self.tavily = TavilyTool()
        self.groq = GroqTool()
        self.database = DatabaseTool()
        self.email = EmailTool()
        self.calendar = CalendarTool()
        
        # Build workflow graph
        self.graph = self._build_workflow()
        self.app = self.graph.compile()
    
    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow with 8 nodes."""
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("calendar_check", self.calendar_check_node)
        workflow.add_node("query_analysis", self.query_analysis_node)
        workflow.add_node("search", self.search_node)
        workflow.add_node("deduplication", self.deduplication_node)
        workflow.add_node("summarize", self.summarize_node)
        workflow.add_node("store", self.store_node)
        workflow.add_node("format", self.format_node)
        workflow.add_node("email", self.email_node)
        
        # Define edges
        workflow.set_entry_point("calendar_check")
        
        workflow.add_conditional_edges(
            "calendar_check",
            self.should_continue_after_calendar,
            {
                "continue": "query_analysis",
                "skip": END,
            }
        )
        
        workflow.add_edge("query_analysis", "search")
        
        workflow.add_conditional_edges(
            "search",
            self.should_continue_after_search,
            {
                "continue": "deduplication",
                "skip": END,
            }
        )
        
        workflow.add_edge("deduplication", "summarize")
        
        workflow.add_conditional_edges(
            "summarize",
            self.should_continue_after_summarize,
            {
                "continue": "store",
                "skip": END,
            }
        )
        
        workflow.add_edge("store", "format")
        workflow.add_edge("format", "email")
        workflow.add_edge("email", END)
        
        return workflow
    
    def calendar_check_node(self, state: AgentState) -> AgentState:
        """Node 1: Validate if it's time to send."""
        logger.info("Node 1: Calendar Check")
        
        # Initialize state fields if missing
        if "errors" not in state:
            state["errors"] = []
        if "metadata" not in state:
            state["metadata"] = {}
        
        try:
            preferences = state.get("user_preferences", {})
            timezone = preferences.get("timezone", "UTC")
            schedule_time = preferences.get("schedule_time", "09:00")
            
            is_valid = self.calendar.validate_send_time(timezone, schedule_time)
            
            if not is_valid:
                state["errors"].append("Not scheduled time yet")
                logger.info("Calendar check: Not scheduled time, skipping")
            
            state["metadata"]["calendar_check_passed"] = is_valid
            
        except Exception as e:
            logger.error(f"Calendar check failed: {str(e)}")
            state["errors"].append(f"Calendar check error: {str(e)}")
            state["metadata"]["calendar_check_passed"] = False
        
        return state
    
    def query_analysis_node(self, state: AgentState) -> AgentState:
        """Node 2: Generate search queries from preferences."""
        logger.info("Node 2: Query Analysis")
        
        # Initialize state fields if missing
        if "errors" not in state:
            state["errors"] = []
        if "metadata" not in state:
            state["metadata"] = {}
        
        try:
            preferences = state.get("user_preferences", {})
            queries = self.groq.analyze_preferences(preferences)
            
            state["search_queries"] = queries
            state["metadata"]["queries_generated"] = len(queries)
            
            logger.info(f"Generated {len(queries)} search queries")
            
        except Exception as e:
            logger.error(f"Query analysis failed: {str(e)}")
            state["errors"].append(f"Query analysis error: {str(e)}")
            # Fallback: use topics directly
            topics = preferences.get("topics", [])
            state["search_queries"] = [f"{topic} news" for topic in topics[:2]]
        
        return state
    
    def search_node(self, state: AgentState) -> AgentState:
        """Node 3: Execute Tavily searches."""
        logger.info("Node 3: Search")
        
        # Initialize state fields if missing
        if "errors" not in state:
            state["errors"] = []
        if "metadata" not in state:
            state["metadata"] = {}
        
        articles = []
        queries = state.get("search_queries", [])
        
        for query in queries:
            try:
                results = self.tavily.search_news(query, max_results=5)
                articles.extend(results)
                logger.info(f"Search query '{query}': {len(results)} articles")
            except Exception as e:
                logger.error(f"Search failed for query '{query}': {str(e)}")
                state["errors"].append(f"Search error for '{query}': {str(e)}")
        
        state["articles"] = articles
        state["metadata"]["articles_found"] = len(articles)
        
        return state
    
    def deduplication_node(self, state: AgentState) -> AgentState:
        """Node 4: Filter duplicates."""
        logger.info("Node 4: Deduplication")
        
        articles = state.get("articles", [])
        user_email = state.get("user_email", "")
        deduplicated = []
        
        for article in articles:
            # Generate article hash
            article_hash = self.database.get_article_hash(article)
            article_id = article.get("url", article_hash)
            
            # Check article-level deduplication
            if self.database.check_article_hash(article_hash):
                logger.debug(f"Article duplicate (hash): {article.get('title', '')[:50]}")
                continue
            
            # Check user-level deduplication
            if self.database.check_user_history(user_email, article_id):
                logger.debug(f"Article already sent to user: {article.get('title', '')[:50]}")
                continue
            
            # Add article ID for tracking
            article["article_id"] = article_id
            article["article_hash"] = article_hash
            deduplicated.append(article)
        
        state["deduplicated_articles"] = deduplicated
        state["metadata"]["duplicates_filtered"] = len(articles) - len(deduplicated)
        state["metadata"]["articles_after_dedup"] = len(deduplicated)
        
        logger.info(f"Deduplication: {len(articles)} -> {len(deduplicated)} articles")
        
        return state
    
    def summarize_node(self, state: AgentState) -> AgentState:
        """Node 5: Generate summaries."""
        logger.info("Node 5: Summarize")
        
        # Initialize state fields if missing
        if "errors" not in state:
            state["errors"] = []
        if "metadata" not in state:
            state["metadata"] = {}
        
        articles = state.get("deduplicated_articles", [])
        preferences = state.get("user_preferences", {})
        summaries = []
        
        for article in articles:
            try:
                summary_text = self.groq.summarize_article(article, preferences)
                summaries.append({
                    "title": article.get("title", ""),
                    "url": article.get("url", ""),
                    "summary": summary_text,
                    "article_id": article.get("article_id"),
                    "article_hash": article.get("article_hash"),
                })
            except Exception as e:
                logger.error(f"Summarization failed for article: {str(e)}")
                state["errors"].append(f"Summarization error: {str(e)}")
                # Skip this article
                continue
        
        state["summaries"] = summaries
        state["metadata"]["summaries_generated"] = len(summaries)
        
        logger.info(f"Generated {len(summaries)} summaries")
        
        return state
    
    def store_node(self, state: AgentState) -> AgentState:
        """Node 6: Store articles in database."""
        logger.info("Node 6: Store")
        
        # Initialize state fields if missing
        if "errors" not in state:
            state["errors"] = []
        if "metadata" not in state:
            state["metadata"] = {}
        
        summaries = state.get("summaries", [])
        
        for item in summaries:
            try:
                article_hash = item.get("article_hash")
                if article_hash:
                    # Reconstruct article dict for storage
                    article = {
                        "title": item.get("title"),
                        "url": item.get("url"),
                    }
                    self.database.store_article(article, article_hash)
            except Exception as e:
                logger.error(f"Storage failed: {str(e)}")
                state["errors"].append(f"Storage error: {str(e)}")
        
        state["metadata"]["articles_stored"] = len(summaries)
        
        return state
    
    def format_node(self, state: AgentState) -> AgentState:
        """Node 7: Format email content."""
        logger.info("Node 7: Format")
        
        # Initialize state fields if missing
        if "errors" not in state:
            state["errors"] = []
        if "metadata" not in state:
            state["metadata"] = {}
        
        try:
            summaries = state.get("summaries", [])
            preferences = state.get("user_preferences", {})
            
            html_content = self.groq.generate_email_content(summaries, preferences)
            state["email_content"] = html_content
            
            logger.info("Email content formatted")
            
        except Exception as e:
            logger.error(f"Email formatting failed: {str(e)}")
            state["errors"].append(f"Email formatting error: {str(e)}")
            # Fallback: simple HTML
            state["email_content"] = "<html><body><p>Error generating email content.</p></body></html>"
        
        return state
    
    def email_node(self, state: AgentState) -> AgentState:
        """Node 8: Send email."""
        logger.info("Node 8: Email")
        
        # Initialize state fields if missing
        if "errors" not in state:
            state["errors"] = []
        if "metadata" not in state:
            state["metadata"] = {}
        
        try:
            user_email = state.get("user_email", "")
            email_content = state.get("email_content", "")
            
            if not email_content:
                logger.warning("No email content to send")
                return state
            
            subject = "Your Daily AI Briefing"
            result = self.email.send_email(user_email, subject, email_content)
            
            # Mark articles as sent to user
            summaries = state.get("summaries", [])
            for item in summaries:
                article_id = item.get("article_id")
                if article_id:
                    self.database.mark_sent_to_user(user_email, article_id)
            
            state["metadata"]["email_sent"] = True
            state["metadata"]["email_message_id"] = result.get("message_id")
            
            logger.info(f"Email sent to {user_email}")
            
        except Exception as e:
            logger.error(f"Email sending failed: {str(e)}")
            state["errors"].append(f"Email error: {str(e)}")
            state["metadata"]["email_sent"] = False
        
        return state
    
    def should_continue_after_calendar(self, state: AgentState) -> Literal["continue", "skip"]:
        """Conditional: Continue after calendar check?"""
        passed = state.get("metadata", {}).get("calendar_check_passed", False)
        return "continue" if passed else "skip"
    
    def should_continue_after_search(self, state: AgentState) -> Literal["continue", "skip"]:
        """Conditional: Continue after search?"""
        articles = state.get("articles", [])
        return "continue" if articles else "skip"
    
    def should_continue_after_summarize(self, state: AgentState) -> Literal["continue", "skip"]:
        """Conditional: Continue after summarize?"""
        summaries = state.get("summaries", [])
        return "continue" if summaries else "skip"


def create_agent():
    """
    Create and return compiled LangGraph agent.
    
    Returns:
        Compiled LangGraph application
    """
    workflow = BriefingAgentWorkflow()
    return workflow.app
