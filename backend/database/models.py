"""
Database models for Digestible
"""

import enum
import uuid

from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    String,
    Text,
)
from sqlalchemy import (
    Enum as SQLEnum,
)
from sqlalchemy.sql import func

from .connection import Base


class ArticleStatus(str, enum.Enum):
    """Processing pipeline status"""

    PENDING = "PENDING"
    FETCHING = "FETCHING"
    PARSING = "PARSING"
    CHUNKING = "CHUNKING"
    SUMMARIZING = "SUMMARIZING"
    RENDERING = "RENDERING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class Article(Base):
    """
    Article model for ingestion pipeline
    Tracks status through each pipeline stage
    """

    __tablename__ = "articles"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False, index=True)
    url = Column(String, nullable=False, unique=True)

    # Content
    title = Column(String, nullable=True)
    raw_html = Column(Text, nullable=True)
    parsed_text = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)

    # Pipeline tracking
    status = Column(SQLEnum(ArticleStatus), default=ArticleStatus.PENDING, nullable=False)
    error_message = Column(Text, nullable=True)

    # Metadata
    word_count = Column(Integer, nullable=True)
    chunk_count = Column(Integer, nullable=True)

    # Timestamps
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    completed_at = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<Article(id='{self.id}', url='{self.url[:50]}...', status='{self.status}')>"
