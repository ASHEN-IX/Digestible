# Backend Integration Tests
import os
import time

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.orm import sessionmaker

from backend.database.connection import get_db
from backend.database.models import Article, ArticleStatus
from backend.main import app

# Set test database URL before importing models
os.environ["DATABASE_URL"] = "sqlite:///:memory:"


@pytest.fixture(scope="session")
def test_db_engine():
    """Create in-memory SQLite database for tests"""
    from sqlalchemy import create_engine

    from backend.database.models import Base

    engine = create_engine(
        "sqlite:///:memory:", echo=False, connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(scope="function")
def test_db_session(test_db_engine):
    """Create test database session"""
    from backend.database.connection import SessionLocal

    # Temporarily replace the global SessionLocal with test session factory
    original_sessionmaker = SessionLocal
    test_sessionmaker = sessionmaker(autocommit=False, autoflush=False, bind=test_db_engine)

    # Monkey patch the global SessionLocal
    import backend.database.connection

    backend.database.connection.SessionLocal = test_sessionmaker

    # Create tables in test database
    from backend.database.models import Base

    Base.metadata.create_all(bind=test_db_engine)

    session = test_sessionmaker()
    try:
        yield session
    finally:
        session.rollback()
        session.close()
        # Restore original SessionLocal
        backend.database.connection.SessionLocal = original_sessionmaker


class TestArticleProcessingPipeline:
    """Integration tests for the complete article processing pipeline"""

    @pytest.mark.asyncio
    async def test_article_submission_and_storage(self, test_db_session):
        """Test article submission and database storage"""

        # Override the database dependency
        def override_get_db():
            yield test_db_session

        app.dependency_overrides[get_db] = override_get_db

        try:
            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://testserver"
            ) as client:
                # Submit article
                unique_url = f"https://example.com/test-integration-{int(time.time())}"
                response = await client.post(
                    "/api/v1/articles", json={"url": unique_url, "user_id": "integration_test"}
                )

                assert response.status_code == 201
                data = response.json()
                assert "id" in data
                article_id = data["id"]
                assert data["status"] == "PENDING"

                # Verify article was created in test database
                article = test_db_session.query(Article).filter(Article.id == article_id).first()
                assert article is not None
                assert article.status == ArticleStatus.PENDING
                assert article.url == unique_url

        finally:
            # Clean up dependency override
            app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_article_retrieval(self, test_db_session):
        """Test article status retrieval"""

        # Override the database dependency
        def override_get_db():
            yield test_db_session

        app.dependency_overrides[get_db] = override_get_db

        try:
            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://testserver"
            ) as client:
                # First submit an article
                unique_url = f"https://example.com/test-get-{int(time.time())}"
                submit_response = await client.post(
                    "/api/v1/articles", json={"url": unique_url, "user_id": "test_user"}
                )
                assert submit_response.status_code == 201
                article_data = submit_response.json()
                article_id = article_data["id"]

                # Then retrieve it
                get_response = await client.get(f"/api/v1/articles/{article_id}")
                assert get_response.status_code == 200
                data = get_response.json()
                assert data["id"] == article_id
                assert "status" in data
                assert "url" in data
                assert data["url"] == unique_url

        finally:
            # Clean up dependency override
            app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_health_and_root_endpoints(self):
        """Test basic API endpoints work"""
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://testserver"
        ) as client:
            # Test root endpoint
            response = await client.get("/")
            assert response.status_code == 200
            data = response.json()
            assert data["app"] == "Digestible"
            assert data["status"] == "operational"

            # Test health endpoint
            response = await client.get("/health")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
