"""
FastAPI application main entry point
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api import articles_router
from backend.config import get_settings

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
def health():
    """
    Detailed health check
    """
    return {
        "status": "healthy",
        "database": "connected",  # TODO: Add actual DB check
        "redis": "connected",  # TODO: Add actual Redis check
    }
