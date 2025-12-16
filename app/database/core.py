# app/database/core.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import os

# --- 1. Connection String Assembly ---
def get_db_url(is_sync: bool = False) -> str:
    """Assembles the connection string based on environment variables.
       'is_sync=True' is used specifically for Alembic's internal connection.
    """
    
    # Choose driver prefix: 'postgresql+asyncpg' for application, 'postgresql' for Alembic
    driver = "postgresql" + ("+asyncpg" if not is_sync else "")

    # Priority 1: CI/Production (using the single Neon URL)
    neon_url = os.environ.get("NEON_DATABASE_URL")
    if neon_url:
        return neon_url.replace("postgresql://", f"{driver}://")

    # Priority 2: Local Development (using separate Docker Compose variables)
    db_host = os.environ.get("DB_HOST")
    if db_host:
        return (f"{driver}://{os.environ['DB_USER']}:{os.environ['DB_PASSWORD']}@"
                f"{db_host}:{os.environ.get('DB_PORT', '5432')}/{os.environ['DB_NAME']}")
    
    raise ValueError("Database configuration environment variables missing. Did you forget to set DB_HOST or NEON_DATABASE_URL?")

# --- 2. Engine and Session Setup (Used by FastAPI) ---
# NOTE: We use the async driver here
ASYNC_DATABASE_URL = get_db_url()

engine = create_async_engine(
    ASYNC_DATABASE_URL, 
    echo=False, # Set to True to see SQL logs
)

AsyncSessionLocal = sessionmaker(
    bind=engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

# --- 3. Dependency Injection (Used by FastAPI) ---
async def get_session() -> AsyncSession:
    """Dependency injector for FastAPI routes."""
    async with AsyncSessionLocal() as session:
        yield session