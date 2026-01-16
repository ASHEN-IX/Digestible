"""
API routes for article ingestion
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, HttpUrl
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.database import Article, ArticleStatus, get_db
from backend.tasks import process_article_task

router = APIRouter(prefix="/api/v1", tags=["articles"])


class ArticleSubmission(BaseModel):
    """Request model for article submission"""

    url: HttpUrl
    user_id: str = "anonymous"  # Placeholder until auth is implemented


class ArticleResponse(BaseModel):
    """Response model for article operations"""

    id: str
    url: str
    status: str
    title: Optional[str] = None
    summary: Optional[str] = None
    created_at: str


@router.post("/articles", response_model=ArticleResponse, status_code=201)
def submit_article(
    submission: ArticleSubmission,
    db: Session = Depends(get_db),
):
    """
    Submit a new article for processing
    Processes asynchronously in background
    """
    # Check if URL already exists

    result = db.execute(select(Article).where(Article.url == str(submission.url)))
    existing = result.scalar_one_or_none()

    if existing:
        raise HTTPException(
            status_code=409, detail=f"Article already exists with ID: {existing.id}"
        )

    # Create new article
    article = Article(
        url=str(submission.url),
        user_id=submission.user_id,
        status=ArticleStatus.PENDING,
    )

    db.add(article)
    db.commit()
    db.refresh(article)

    # Start async processing task
    process_article_task.delay(article.id)

    return ArticleResponse(
        id=article.id,
        url=article.url,
        status=article.status.value,
        title=article.title,
        summary=article.summary,
        created_at=article.created_at.isoformat(),
    )


@router.get("/articles", response_model=list[ArticleResponse])
def list_articles(db: Session = Depends(get_db)):
    """
    List all articles
    """
    from sqlalchemy import select

    result = db.execute(select(Article).order_by(Article.created_at.desc()))
    articles = result.scalars().all()

    return [
        ArticleResponse(
            id=article.id,
            url=article.url,
            status=article.status.value,
            title=article.title,
            summary=article.summary,
            created_at=article.created_at.isoformat(),
        )
        for article in articles
    ]


@router.get("/articles/{article_id}", response_model=ArticleResponse)
def get_article(article_id: str, db: Session = Depends(get_db)):
    """
    Get article status and content
    """
    from sqlalchemy import select

    result = db.execute(select(Article).where(Article.id == article_id))
    article = result.scalar_one_or_none()

    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    return ArticleResponse(
        id=article.id,
        url=article.url,
        status=article.status.value,
        title=article.title,
        summary=article.summary,
        created_at=article.created_at.isoformat(),
    )


@router.delete("/articles/{article_id}", status_code=204)
def delete_article(article_id: str, db: Session = Depends(get_db)):
    """
    Delete an article
    """
    from sqlalchemy import delete as sql_delete
    from sqlalchemy import select

    result = db.execute(select(Article).where(Article.id == article_id))
    article = result.scalar_one_or_none()

    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    db.execute(sql_delete(Article).where(Article.id == article_id))
    db.commit()

    return None


@router.get("/articles/{article_id}/audio")
def get_article_audio(article_id: str, db: Session = Depends(get_db)):
    """
    Get audio file for an article
    """
    from pathlib import Path

    # Get article from database
    result = db.execute(select(Article).where(Article.id == article_id))
    article = result.scalar_one_or_none()

    if not article or not article.audio_path:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Audio not found")

    # Check if file exists
    audio_file = Path(article.audio_path)
    if not audio_file.exists():
        raise HTTPException(status_code=404, detail="Audio file not found")

    # Return file
    from fastapi.responses import FileResponse

    # Determine media type based on file extension
    media_type = "audio/mpeg" if audio_file.suffix.lower() == ".mp3" else "audio/wav"
    filename = f"article_{article_id}{audio_file.suffix}"

    return FileResponse(path=audio_file, media_type=media_type, filename=filename)
