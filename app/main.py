"""FastAPI application for AI Briefing Agent."""
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session
from database import get_db, init_db, db_manager, User, Article, UserArticle
from app.scheduler import start_scheduler, shutdown_scheduler, schedule_user_briefing, unschedule_user_briefing, get_scheduled_jobs
from app.agent_runner import agent_runner
from config import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="AI Briefing Agent API",
    description="Serverless AI agent that delivers personalized news briefings",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic models for request/response
class UserPreferences(BaseModel):
    """User preferences model."""
    topics: List[str] = Field(..., min_items=1, description="List of topics to follow")


class RegisterRequest(BaseModel):
    """User registration request."""
    email: EmailStr
    preferences: UserPreferences
    timezone: str = Field(default="UTC", description="User timezone (e.g., America/New_York)")
    briefing_time: str = Field(default="09:00", pattern=r"^\d{2}:\d{2}$", description="Briefing time in HH:MM format")


class UpdatePreferencesRequest(BaseModel):
    """Update user preferences request."""
    preferences: Optional[UserPreferences] = None
    timezone: Optional[str] = None
    briefing_time: Optional[str] = Field(None, pattern=r"^\d{2}:\d{2}$")


class QueryRequest(BaseModel):
    """Real-time query request."""
    email: EmailStr
    query: str = Field(..., min_length=1, description="Search query")
    max_results: int = Field(default=5, ge=1, le=20, description="Maximum number of results")


class ArticleResponse(BaseModel):
    """Article response model."""
    title: str
    url: str
    summary: str


class QueryResponse(BaseModel):
    """Query response model."""
    success: bool
    query: str
    articles: List[ArticleResponse]
    total_found: int
    total_returned: int
    errors: List[str] = []


class UserResponse(BaseModel):
    """User response model."""
    email: str
    preferences: Dict[str, Any]
    timezone: str
    briefing_time: str
    created_at: datetime


class MetricsResponse(BaseModel):
    """User metrics response."""
    email: str
    total_articles_sent: int
    last_briefing_at: Optional[datetime]
    topics: List[str]
    created_at: datetime


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    database: str
    scheduler: str
    timestamp: datetime


# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize database and start scheduler on startup."""
    logger.info("Starting AI Briefing Agent API...")
    
    # Initialize database
    try:
        init_db()
        logger.info("✓ Database initialized")
    except Exception as e:
        logger.error(f"✗ Database initialization failed: {str(e)}")
    
    # Start scheduler
    try:
        start_scheduler()
        logger.info("✓ Scheduler started")
    except Exception as e:
        logger.error(f"✗ Scheduler start failed: {str(e)}")
    
    logger.info("AI Briefing Agent API started successfully")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown scheduler gracefully."""
    logger.info("Shutting down AI Briefing Agent API...")
    shutdown_scheduler()
    logger.info("AI Briefing Agent API shutdown complete")


# API Endpoints

@app.get("/", tags=["Root"])
async def root():
    """Root endpoint."""
    return {
        "message": "AI Briefing Agent API",
        "version": "2.0.0",
        "docs": "/docs"
    }


@app.get("/api/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint."""
    db_status = "connected" if db_manager.health_check() else "disconnected"
    
    # Check scheduler
    from app.scheduler import scheduler
    scheduler_status = "running" if scheduler.running else "stopped"
    
    return {
        "status": "healthy" if db_status == "connected" else "unhealthy",
        "database": db_status,
        "scheduler": scheduler_status,
        "timestamp": datetime.utcnow()
    }


@app.post("/api/register", status_code=status.HTTP_201_CREATED, tags=["Users"])
async def register_user(request: RegisterRequest, db: Session = Depends(get_db)):
    """Register a new user and schedule their briefing."""
    logger.info(f"Registering user: {request.email}")
    
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == request.email).first()
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already registered. Use PUT /api/preferences/{email} to update."
            )
        
        # Create new user
        new_user = User(
            email=request.email,
            preferences={"topics": request.preferences.topics},
            timezone=request.timezone,
            briefing_time=request.briefing_time,
            created_at=datetime.utcnow()
        )
        db.add(new_user)
        db.commit()
        
        # Schedule briefing
        schedule_success = schedule_user_briefing(
            request.email,
            request.timezone,
            request.briefing_time
        )
        
        if not schedule_success:
            logger.warning(f"Failed to schedule briefing for {request.email}")
        
        # Send confirmation email (optional)
        # TODO: Implement confirmation email
        
        logger.info(f"✓ User registered: {request.email}")
        
        return {
            "status": "registered",
            "user_email": request.email,
            "message": f"Daily briefing scheduled for {request.briefing_time} {request.timezone}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error registering user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to register user: {str(e)}"
        )


@app.get("/api/preferences/{email}", response_model=UserResponse, tags=["Users"])
async def get_preferences(email: str, db: Session = Depends(get_db)):
    """Get user preferences."""
    user = db.query(User).filter(User.email == email).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {
        "email": user.email,
        "preferences": user.preferences,
        "timezone": user.timezone,
        "briefing_time": user.briefing_time,
        "created_at": user.created_at
    }


@app.put("/api/preferences/{email}", tags=["Users"])
async def update_preferences(
    email: str,
    request: UpdatePreferencesRequest,
    db: Session = Depends(get_db)
):
    """Update user preferences and reschedule briefing."""
    user = db.query(User).filter(User.email == email).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    try:
        # Update preferences
        if request.preferences:
            user.preferences = {"topics": request.preferences.topics}
        
        if request.timezone:
            user.timezone = request.timezone
        
        if request.briefing_time:
            user.briefing_time = request.briefing_time
        
        db.commit()
        
        # Reschedule briefing if time or timezone changed
        if request.timezone or request.briefing_time:
            schedule_user_briefing(user.email, user.timezone, user.briefing_time)
        
        logger.info(f"✓ Updated preferences for {email}")
        
        return {
            "status": "updated",
            "user_email": email,
            "message": "Preferences updated successfully"
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating preferences: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update preferences: {str(e)}"
        )


@app.delete("/api/preferences/{email}", status_code=status.HTTP_204_NO_CONTENT, tags=["Users"])
async def delete_user(email: str, db: Session = Depends(get_db)):
    """Delete user and unschedule briefing."""
    user = db.query(User).filter(User.email == email).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    try:
        # Unschedule briefing
        unschedule_user_briefing(email)
        
        # Delete user (cascade deletes user_articles)
        db.delete(user)
        db.commit()
        
        logger.info(f"✓ Deleted user: {email}")
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete user: {str(e)}"
        )


@app.post("/api/query", response_model=QueryResponse, tags=["Search"])
async def real_time_query(request: QueryRequest):
    """Execute real-time search query."""
    logger.info(f"Real-time query from {request.email}: '{request.query}'")
    
    try:
        result = agent_runner.run_real_time_query(
            request.email,
            request.query,
            request.max_results
        )
        
        if not result.get("success"):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get("error", "Query failed")
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error executing query: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Query execution failed: {str(e)}"
        )


@app.get("/api/metrics/{email}", response_model=MetricsResponse, tags=["Metrics"])
async def get_user_metrics(email: str, db: Session = Depends(get_db)):
    """Get user metrics."""
    user = db.query(User).filter(User.email == email).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Get total articles sent
    total_articles = db.query(UserArticle).filter(
        UserArticle.user_email == email
    ).count()
    
    # Get last briefing time
    last_article = db.query(UserArticle).filter(
        UserArticle.user_email == email
    ).order_by(UserArticle.sent_at.desc()).first()
    
    last_briefing_at = last_article.sent_at if last_article else None
    
    return {
        "email": user.email,
        "total_articles_sent": total_articles,
        "last_briefing_at": last_briefing_at,
        "topics": user.preferences.get("topics", []),
        "created_at": user.created_at
    }


@app.get("/api/users", response_model=List[UserResponse], tags=["Users"])
async def get_all_users(db: Session = Depends(get_db)):
    """Get all registered users."""
    users = db.query(User).order_by(User.created_at.desc()).all()
    
    return [
        {
            "email": user.email,
            "preferences": user.preferences,
            "timezone": user.timezone,
            "briefing_time": user.briefing_time,
            "created_at": user.created_at
        }
        for user in users
    ]


@app.get("/api/admin/jobs", tags=["Admin"])
async def get_scheduled_jobs_endpoint():
    """Get all scheduled jobs (admin endpoint)."""
    jobs = get_scheduled_jobs()
    return {
        "total_jobs": len(jobs),
        "jobs": jobs
    }


@app.post("/api/admin/trigger-briefing/{email}", tags=["Admin"])
async def trigger_briefing_manually(email: str, db: Session = Depends(get_db)):
    """Manually trigger briefing for a user (admin endpoint)."""
    user = db.query(User).filter(User.email == email).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    try:
        result = agent_runner.run_scheduled_briefing(email)
        return result
        
    except Exception as e:
        logger.error(f"Error triggering briefing: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to trigger briefing: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
