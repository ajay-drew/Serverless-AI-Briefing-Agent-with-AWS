"""Unit tests for FastAPI endpoints."""
import pytest
from unittest.mock import Mock, MagicMock, patch, PropertyMock
from fastapi.testclient import TestClient
from datetime import datetime


@pytest.mark.unit
class TestFastAPIEndpoints:
    """Unit tests for FastAPI application endpoints."""
    
    @pytest.fixture
    def client(self):
        """Create FastAPI test client with mocked dependencies."""
        # Mock all the imports and dependencies before importing app
        with patch('database.db_manager'), \
             patch('app.scheduler.scheduler'), \
             patch('app.agent_runner.agent_runner'):
            
            # Now import the app
            from app import main
            
            # Override the on_event decorators to prevent startup/shutdown
            with patch.object(main.app, 'on_event', return_value=lambda f: f):
                client = TestClient(main.app)
                yield client
    
    def test_root_endpoint(self, client):
        """Test root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "AI Briefing Agent API"
        assert "version" in data
        assert "docs" in data
    
    def test_health_check_healthy(self, client):
        """Test health check endpoint when healthy."""
        with patch('app.main.db_manager.health_check', return_value=True), \
             patch('app.main.scheduler.running', True):
            response = client.get("/api/health")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
            assert data["database"] == "connected"
            assert data["scheduler"] == "running"
    
    def test_health_check_unhealthy(self, client):
        """Test health check endpoint when database is down."""
        with patch('app.main.db_manager.health_check', return_value=False), \
             patch('app.main.scheduler.running', True):
            response = client.get("/api/health")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "unhealthy"
            assert data["database"] == "disconnected"
    
    def test_register_user_success(self, client):
        """Test successful user registration."""
        with patch('app.main.schedule_user_briefing', return_value=True):
            response = client.post("/api/register", json={
                "email": "newuser@example.com",
                "preferences": {"topics": ["AI", "tech"]},
                "timezone": "UTC",
                "briefing_time": "09:00"
            })
            
            assert response.status_code == 201
            data = response.json()
            assert data["status"] == "registered"
            assert data["user_email"] == "newuser@example.com"
    
    def test_register_user_already_exists(self, client, test_db_engine):
        """Test registering user that already exists."""
        from database import User
        from sqlalchemy.orm import Session
        
        # Create existing user
        session = Session(bind=test_db_engine)
        user = User(
            email="existing@example.com",
            preferences={"topics": ["AI"]},
            timezone="UTC",
            briefing_time="09:00",
            created_at=datetime.utcnow()
        )
        session.add(user)
        session.commit()
        session.close()
        
        response = client.post("/api/register", json={
            "email": "existing@example.com",
            "preferences": {"topics": ["AI"]},
            "timezone": "UTC",
            "briefing_time": "09:00"
        })
        
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"]
    
    def test_register_user_invalid_data(self, client):
        """Test registration with invalid data."""
        response = client.post("/api/register", json={
            "email": "invalid-email",
            "preferences": {"topics": []},  # Empty topics
            "timezone": "UTC",
            "briefing_time": "09:00"
        })
        
        assert response.status_code == 422  # Validation error
    
    def test_get_preferences_success(self, client, test_db_engine):
        """Test getting user preferences."""
        from database import User
        from sqlalchemy.orm import Session
        
        # Create user
        session = Session(bind=test_db_engine)
        user = User(
            email="getprefs@example.com",
            preferences={"topics": ["AI"]},
            timezone="UTC",
            briefing_time="09:00",
            created_at=datetime.utcnow()
        )
        session.add(user)
        session.commit()
        session.close()
        
        response = client.get("/api/preferences/getprefs@example.com")
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "getprefs@example.com"
        assert data["timezone"] == "UTC"
    
    def test_get_preferences_not_found(self, client):
        """Test getting preferences for non-existent user."""
        response = client.get("/api/preferences/nonexistent@example.com")
        assert response.status_code == 404
    
    def test_update_preferences_success(self, client, test_db_engine):
        """Test updating user preferences."""
        from database import User
        from sqlalchemy.orm import Session
        
        # Create user
        session = Session(bind=test_db_engine)
        user = User(
            email="updateuser@example.com",
            preferences={"topics": ["AI"]},
            timezone="UTC",
            briefing_time="09:00",
            created_at=datetime.utcnow()
        )
        session.add(user)
        session.commit()
        session.close()
        
        with patch('app.main.schedule_user_briefing', return_value=True):
            response = client.put("/api/preferences/updateuser@example.com", json={
                "preferences": {"topics": ["AI", "ML"]},
                "timezone": "America/New_York"
            })
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "updated"
    
    def test_delete_user_success(self, client, test_db_engine):
        """Test deleting user."""
        from database import User
        from sqlalchemy.orm import Session
        
        # Create user
        session = Session(bind=test_db_engine)
        user = User(
            email="deleteuser@example.com",
            preferences={"topics": ["AI"]},
            timezone="UTC",
            briefing_time="09:00",
            created_at=datetime.utcnow()
        )
        session.add(user)
        session.commit()
        session.close()
        
        with patch('app.main.unschedule_user_briefing', return_value=True):
            response = client.delete("/api/preferences/deleteuser@example.com")
            assert response.status_code == 204
    
    def test_real_time_query_success(self, client):
        """Test real-time query endpoint."""
        with patch('app.main.agent_runner.run_real_time_query') as mock_run:
            mock_run.return_value = {
                "success": True,
                "query": "AI news",
                "articles": [
                    {"title": "Test", "url": "http://test.com", "summary": "Test summary"}
                ],
                "total_found": 5,
                "total_returned": 1,
                "errors": []
            }
            
            response = client.post("/api/query", json={
                "email": "test@example.com",
                "query": "AI news",
                "max_results": 5
            })
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert len(data["articles"]) == 1
    
    def test_get_metrics_success(self, client, test_db_engine):
        """Test getting user metrics."""
        from database import User, Article, UserArticle
        from sqlalchemy.orm import Session
        
        # Create user
        session = Session(bind=test_db_engine)
        user = User(
            email="metrics@example.com",
            preferences={"topics": ["AI"]},
            timezone="UTC",
            briefing_time="09:00",
            created_at=datetime.utcnow()
        )
        session.add(user)
        
        # Create articles
        for i in range(3):
            article = Article(
                id=f"article_{i}",
                url_hash=f"hash_{i}",
                title=f"Article {i}",
                url=f"http://test{i}.com",
                summary=f"Summary {i}",
                created_at=datetime.utcnow()
            )
            session.add(article)
            
            user_article = UserArticle(
                user_email="metrics@example.com",
                article_id=f"article_{i}",
                sent_at=datetime.utcnow()
            )
            session.add(user_article)
        
        session.commit()
        session.close()
        
        response = client.get("/api/metrics/metrics@example.com")
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "metrics@example.com"
        assert data["total_articles_sent"] == 3
    
    def test_admin_get_jobs(self, client):
        """Test admin endpoint to get scheduled jobs."""
        with patch('app.main.get_scheduled_jobs', return_value=[
            {"id": "job1", "name": "Test Job", "next_run_time": None, "trigger": "cron"}
        ]):
            response = client.get("/api/admin/jobs")
            assert response.status_code == 200
            data = response.json()
            assert data["total_jobs"] == 1
    
    def test_admin_trigger_briefing(self, client, test_db_engine):
        """Test manually triggering a briefing."""
        from database import User
        from sqlalchemy.orm import Session
        
        # Create user
        session = Session(bind=test_db_engine)
        user = User(
            email="trigger@example.com",
            preferences={"topics": ["AI"]},
            timezone="UTC",
            briefing_time="09:00",
            created_at=datetime.utcnow()
        )
        session.add(user)
        session.commit()
        session.close()
        
        with patch('app.main.agent_runner.run_scheduled_briefing') as mock_run:
            mock_run.return_value = {
                "success": True,
                "user_email": "trigger@example.com",
                "articles_sent": 5
            }
            
            response = client.post("/api/admin/trigger-briefing/trigger@example.com")
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
