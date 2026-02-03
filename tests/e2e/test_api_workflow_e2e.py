"""End-to-end tests for complete API workflows."""
import pytest
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
from datetime import datetime


@pytest.mark.e2e
class TestAPIWorkflowE2E:
    """End-to-end tests for complete user workflows."""
    
    @pytest.fixture
    def client(self, test_db_engine):
        """Create FastAPI test client with test database."""
        from database import Base, db_manager
        from sqlalchemy.orm import Session
        
        # Create tables
        Base.metadata.create_all(bind=test_db_engine)
        
        def override_get_db():
            session = Session(bind=test_db_engine)
            try:
                yield session
            finally:
                session.close()
        
        with patch('app.main.init_db'), \
             patch('app.main.start_scheduler'), \
             patch('app.main.get_db', override_get_db):
            from app.main import app
            client = TestClient(app)
            yield client
        
        # Cleanup
        Base.metadata.drop_all(bind=test_db_engine)
    
    @pytest.fixture
    def mock_agent_success(self):
        """Mock successful agent execution."""
        with patch('app.agent_runner.create_agent') as mock_create:
            mock_agent = Mock()
            mock_agent.invoke.return_value = {
                "user_email": "test@example.com",
                "articles": [
                    {"title": f"Article {i}", "url": f"http://test{i}.com"}
                    for i in range(5)
                ],
                "summaries": [
                    {
                        "title": f"Article {i}",
                        "url": f"http://test{i}.com",
                        "summary": f"Summary {i}",
                        "article_id": f"http://test{i}.com",
                        "article_hash": f"hash_{i}"
                    }
                    for i in range(5)
                ],
                "errors": [],
                "metadata": {"email_sent": True, "email_message_id": "test_msg_id"}
            }
            mock_create.return_value = mock_agent
            yield mock_agent
    
    def test_complete_user_registration_workflow(self, client, mock_agent_success):
        """Test complete user registration and briefing workflow."""
        with patch('app.main.schedule_user_briefing', return_value=True):
            # Step 1: Register user
            response = client.post("/api/register", json={
                "email": "newuser@example.com",
                "preferences": {"topics": ["AI", "technology"]},
                "timezone": "America/New_York",
                "briefing_time": "09:00"
            })
            
            assert response.status_code == 201
            data = response.json()
            assert data["status"] == "registered"
            assert data["user_email"] == "newuser@example.com"
            
            # Step 2: Get user preferences
            response = client.get("/api/preferences/newuser@example.com")
            assert response.status_code == 200
            data = response.json()
            assert data["email"] == "newuser@example.com"
            assert "AI" in data["preferences"]["topics"]
            
            # Step 3: Update preferences
            response = client.put("/api/preferences/newuser@example.com", json={
                "preferences": {"topics": ["AI", "ML", "robotics"]},
                "briefing_time": "10:00"
            })
            assert response.status_code == 200
            
            # Step 4: Verify update
            response = client.get("/api/preferences/newuser@example.com")
            data = response.json()
            assert len(data["preferences"]["topics"]) == 3
            assert data["briefing_time"] == "10:00"
    
    def test_real_time_query_workflow(self, client, mock_agent_success):
        """Test real-time query workflow."""
        # Execute query
        response = client.post("/api/query", json={
            "email": "guest@example.com",
            "query": "latest AI breakthroughs",
            "max_results": 5
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["query"] == "latest AI breakthroughs"
        assert len(data["articles"]) > 0
        assert "title" in data["articles"][0]
        assert "url" in data["articles"][0]
        assert "summary" in data["articles"][0]
    
    def test_metrics_workflow(self, client, test_db_session, mock_agent_success):
        """Test user metrics workflow."""
        from database import User, Article, UserArticle
        
        # Create user in database
        user = User(
            email="metrics@example.com",
            preferences={"topics": ["AI"]},
            timezone="UTC",
            briefing_time="09:00",
            created_at=datetime.utcnow()
        )
        test_db_session.add(user)
        
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
            test_db_session.add(article)
            
            # Create user-article relationship
            user_article = UserArticle(
                user_email="metrics@example.com",
                article_id=f"article_{i}",
                sent_at=datetime.utcnow()
            )
            test_db_session.add(user_article)
        
        test_db_session.commit()
        
        # Get metrics
        response = client.get("/api/metrics/metrics@example.com")
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "metrics@example.com"
        assert data["total_articles_sent"] == 3
        assert data["topics"] == ["AI"]
    
    def test_admin_trigger_briefing_workflow(self, client, test_db_session, mock_agent_success):
        """Test admin trigger briefing workflow."""
        from database import User
        
        # Create user
        user = User(
            email="trigger@example.com",
            preferences={"topics": ["AI"]},
            timezone="UTC",
            briefing_time="09:00",
            created_at=datetime.utcnow()
        )
        test_db_session.add(user)
        test_db_session.commit()
        
        # Trigger briefing
        response = client.post("/api/admin/trigger-briefing/trigger@example.com")
        assert response.status_code == 200
        data = response.json()
        assert "success" in data or "user_email" in data
    
    def test_delete_user_workflow(self, client, test_db_session):
        """Test user deletion workflow."""
        from database import User
        
        with patch('app.main.unschedule_user_briefing', return_value=True):
            # Create user
            user = User(
                email="delete@example.com",
                preferences={"topics": ["AI"]},
                timezone="UTC",
                briefing_time="09:00",
                created_at=datetime.utcnow()
            )
            test_db_session.add(user)
            test_db_session.commit()
            
            # Delete user
            response = client.delete("/api/preferences/delete@example.com")
            assert response.status_code == 204
            
            # Verify user is deleted
            response = client.get("/api/preferences/delete@example.com")
            assert response.status_code == 404
    
    def test_health_check_workflow(self, client):
        """Test health check endpoint."""
        with patch('app.main.db_manager.health_check', return_value=True), \
             patch('app.main.scheduler.running', True):
            response = client.get("/api/health")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
            assert data["database"] == "connected"
            assert data["scheduler"] == "running"
    
    def test_error_handling_invalid_email(self, client):
        """Test error handling for invalid email."""
        response = client.post("/api/register", json={
            "email": "invalid-email",
            "preferences": {"topics": ["AI"]},
            "timezone": "UTC",
            "briefing_time": "09:00"
        })
        
        assert response.status_code == 422  # Validation error
    
    def test_error_handling_duplicate_registration(self, client, test_db_session):
        """Test error handling for duplicate registration."""
        from database import User
        
        with patch('app.main.schedule_user_briefing', return_value=True):
            # Create existing user
            user = User(
                email="existing@example.com",
                preferences={"topics": ["AI"]},
                timezone="UTC",
                briefing_time="09:00",
                created_at=datetime.utcnow()
            )
            test_db_session.add(user)
            test_db_session.commit()
            
            # Try to register again
            response = client.post("/api/register", json={
                "email": "existing@example.com",
                "preferences": {"topics": ["tech"]},
                "timezone": "UTC",
                "briefing_time": "10:00"
            })
            
            assert response.status_code == 400
            assert "already registered" in response.json()["detail"]
