# Backend Integration Tests
import time
from unittest.mock import patch

import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.main import app
from backend.database.models import Article, ArticleStatus
from backend.database.connection import Base, get_db


@pytest.fixture(scope="session")
def test_db_engine():
    """Create in-memory SQLite database for tests"""
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(scope="function")
def test_db_session(test_db_engine):
    """Create test database session"""
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_db_engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


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
                    "/api/v1/articles",
                    json={"url": unique_url, "user_id": "integration_test"}
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
                    "/api/v1/articles",
                    json={"url": unique_url, "user_id": "test_user"}
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