"""
FastAPI application main entry point
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from backend.api import articles_router
from backend.config import get_settings
from backend.database import get_db

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan events
    """
    try:
        # Startup
        print(f"🚀 Starting {settings.app_name} API")
        print(f"📊 Environment: {settings.environment}")

        yield

        # Shutdown
        print("👋 Shutting down API")
    except Exception as e:
        print(f"❌ Lifespan error: {e}")
        raise


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="Async article ingestion and processing pipeline",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(articles_router)


@app.get("/")
def root():
    """
    Health check endpoint
    """
    return {
        "app": settings.app_name,
        "version": "0.1.0",
        "status": "operational",
        "environment": settings.environment,
    }


@app.get("/health")
def health(db: Session = Depends(get_db)):
    """
    Detailed health check
    """
    try:
        # Simple database check
        db.execute("SELECT 1")
        db_status = "connected"
    except Exception:
        db_status = "disconnected"
    
    return {
        "status": "healthy" if db_status == "connected" else "unhealthy",
        "database": db_status,
        "redis": "connected",  # TODO: Add actual Redis check
    }
