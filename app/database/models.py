from sqlalchemy import Column, String, DateTime, Text, func
from sqlalchemy.orm import declarative_base
import uuid

# This 'Base' must be imported by Alembic's env.py
Base = declarative_base()

class Article(Base):
    __tablename__ = "articles"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    url = Column(String, nullable=False)
    user_id = Column(String, nullable=False)
    status = Column(String, default="PENDING")  # PENDING, PROCESSING, COMPLETED
    summary = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    def __repr__(self):
        return f"<Article(url='{self.url}', status='{self.status}')>"