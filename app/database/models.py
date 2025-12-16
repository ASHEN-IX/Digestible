# app/database/models.py
from sqlalchemy import Column, String, DateTime, func, Enum
from sqlalchemy.orm import declarative_base
import enum

Base = declarative_base()

# Define an Enum for status tracking (cleaner than raw strings)
class ArticleStatus(enum.Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    
class Article(Base):
    __tablename__ = "articles"

    id = Column(String, primary_key=True, index=True) 
    user_id = Column(String, index=True, nullable=False) 
    
    # Core Data
    original_url = Column(String, nullable=False, index=True)
    title = Column(String, nullable=True)
    
    # State and Content
    status = Column(Enum(ArticleStatus), default=ArticleStatus.PENDING, nullable=False)
    summary_text = Column(String, nullable=True)
    s3_audio_key = Column(String, nullable=True) 
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<Article(id='{self.id}', status='{self.status}')>"