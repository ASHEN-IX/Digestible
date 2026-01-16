# Backend Tests
import time

import pytest
from httpx import AsyncClient

from backend.main import app
from backend.database import get_db


@pytest.mark.asyncio
async def test_health_check():
    """Test health check endpoint"""
    from httpx import ASGITransport
    from unittest.mock import Mock

    # Mock database session
    mock_db = Mock()
    mock_db.execute.return_value = None

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testserver"
    ) as client:
        # Override the database dependency
        def mock_get_db():
            yield mock_db

        app.dependency_overrides[get_db] = mock_get_db

        try:
            response = await client.get("/health")
            assert response.status_code == 200
            data = response.json()
            assert "status" in data
            assert data["status"] == "healthy"
        finally:
            # Clean up
            app.dependency_overrides.pop(get_db, None)


@pytest.mark.asyncio
async def test_root_endpoint():
    """Test root endpoint"""
    from httpx import ASGITransport

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testserver"
    ) as client:
        response = await client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "app" in data
        assert data["app"] == "Digestible"
        assert "status" in data
        assert data["status"] == "operational"


@pytest.mark.asyncio
async def test_submit_article():
    """Test article submission endpoint (for browser extension)"""
    from httpx import ASGITransport

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testserver"
    ) as client:
        # Use timestamp to ensure unique URL
        unique_url = f"https://example.com/test-article-submit-{int(time.time())}"
        response = await client.post(
            "/api/v1/articles", json={"url": unique_url, "user_id": "browser_extension"}
        )
        assert response.status_code == 201  # Created
        data = response.json()
        assert "id" in data
        assert "status" in data
        assert "url" in data
        assert data["url"] == unique_url
        assert data["status"] == "PENDING"  # Processing starts asynchronously


@pytest.mark.asyncio
async def test_get_article():
    """Test getting article status"""
    from httpx import ASGITransport

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testserver"
    ) as client:
        # Use timestamp to ensure unique URL
        unique_url = f"https://example.com/test-article-get-{int(time.time())}"
        # First submit an article
        submit_response = await client.post(
            "/api/v1/articles", json={"url": unique_url, "user_id": "browser_extension"}
        )
        assert submit_response.status_code == 201
        article_data = submit_response.json()
        article_id = article_data["id"]

        # Then get its status
        get_response = await client.get(f"/api/v1/articles/{article_id}")
        assert get_response.status_code == 200
        data = get_response.json()
        assert data["id"] == article_id
        assert "status" in data
        assert "url" in data
