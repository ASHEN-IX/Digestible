"""
Configuration management for Digestible backend
"""
import os
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Application
    app_name: str = "Digestible"
    environment: str = "development"
    debug: bool = True
    
    # Database
    database_url: str
    
    # Redis
    redis_url: str = "redis://redis:6379/0"
    
    # Pipeline
    max_content_length: int = 1_000_000  # 1MB max article size
    chunk_size: int = 1000  # Characters per chunk
    max_chunks: int = 50
    
    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance
    """
    return Settings()
