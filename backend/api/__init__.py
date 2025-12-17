"""
API package initialization
"""

from .articles import router as articles_router

__all__ = ["articles_router"]
