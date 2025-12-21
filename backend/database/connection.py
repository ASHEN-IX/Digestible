"""
Database connection and session management
Synchronous setup using psycopg2
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from backend.config import get_settings

settings = get_settings()

# Create synchronous engine
engine = create_engine(
    settings.database_url,
    echo=settings.debug,
    pool_pre_ping=True,
    pool_size=2,
    max_overflow=5,
    pool_timeout=30,
    pool_recycle=3600,
    connect_args={"connect_timeout": 10},
)

# Synchronous session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

# Base class for models
Base = declarative_base()


def get_db():
    """
    Dependency for FastAPI routes
    Yields a synchronous database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize database tables
    Only used for development/testing
    """
    Base.metadata.create_all(bind=engine)
