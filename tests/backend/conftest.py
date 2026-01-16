"""
Test configuration and fixtures for backend tests
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.database.connection import Base
from backend.config import Settings


@pytest.fixture(scope="session")
def test_settings():
    """Test settings with SQLite database"""
    return Settings(
        app_name="Digestible Test",
        environment="test",
        debug=True,
        database_url="sqlite:///./test.db",
        redis_url="redis://localhost:6379/1",  # Use different DB for tests
        openrouter_api_key="test_key",
        openrouter_base_url="https://openrouter.ai/api/v1"
    )


@pytest.fixture(scope="session")
def test_engine(test_settings):
    """Create test database engine"""
    engine = create_engine(test_settings.database_url, echo=False)
    Base.metadata.create_all(bind=engine)
    yield engine
    # Cleanup
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(scope="function")
def db_session(test_engine):
    """Create test database session"""
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture(scope="function", autouse=True)
def reset_db_engine():
    """
    Reset database engine for each test to avoid connection issues.
    This fixture runs automatically before each test function.
    """
    # For now, just yield - we'll handle engine reset in individual tests if needed
    yield
