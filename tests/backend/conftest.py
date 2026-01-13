"""
Test configuration and fixtures for backend tests
"""

import pytest

from backend.database.connection import engine


@pytest.fixture(scope="function", autouse=True)
def reset_db_engine():
    """
    Reset database engine for each test to avoid connection issues.
    This fixture runs automatically before each test function.
    """
    yield
    # Dispose of the engine's connection pool after each test
    engine.dispose()
