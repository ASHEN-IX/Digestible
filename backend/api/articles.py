"""
API routes for article ingestion
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, HttpUrl
from typing import Optional

from backend.database import get_db, Article, ArticleStatus, AsyncSessionLocal
from backend.pipeline import process_article

router = APIRouter(prefix="/api/v1", tags=["articles"])


async def process_article_with_session(article_id: str):
    """
    Wrapper to process article with its own database session
    This is needed for background tasks
    """
    async with AsyncSessionLocal() as db:
        await process_article(article_id, db)


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


@router.post("/articles", response_model=ArticleResponse, status_code=202)
async def submit_article(
    submission: ArticleSubmission,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """
    Submit a new article for processing
    Returns immediately with article ID
    Processing happens in background
    """
    # Check if URL already exists
    from sqlalchemy import select

    result = await db.execute(select(Article).where(Article.url == str(submission.url)))
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
    await db.commit()
    await db.refresh(article)

    # Store article_id for background processing
    article_id = article.id
    article_data = ArticleResponse(
        id=article.id,
        url=article.url,
        status=article.status.value,
        created_at=article.created_at.isoformat(),
    )

    # Process in background with new session
    background_tasks.add_task(process_article_with_session, article_id)

    return article_data


@router.get("/articles/{article_id}", response_model=ArticleResponse)
async def get_article(article_id: str, db: AsyncSession = Depends(get_db)):
    """
    Get article status and content
    """
    from sqlalchemy import select

    result = await db.execute(select(Article).where(Article.id == article_id))
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
async def delete_article(article_id: str, db: AsyncSession = Depends(get_db)):
    """
    Delete an article
    """
    from sqlalchemy import select, delete as sql_delete

    result = await db.execute(select(Article).where(Article.id == article_id))
    article = result.scalar_one_or_none()

    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    await db.execute(sql_delete(Article).where(Article.id == article_id))
    await db.commit()

    return None
