"""
Pipeline Orchestrator - Coordinates all pipeline stages
"""
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime

from backend.database.models import Article, ArticleStatus
from .fetch import fetch_article
from .parse import parse_article
from .chunk import chunk_article
from .summarize import summarize_article
from .render import render_article


async def process_article(article_id: str, db: AsyncSession) -> bool:
    """
    Process an article through the complete pipeline
    
    Args:
        article_id: Article ID to process
        db: Database session
        
    Returns:
        True if successful, False otherwise
    """
    article = None
    try:
        # Get article from database using SQLAlchemy 2.0 syntax
        result = await db.execute(
            select(Article).where(Article.id == article_id)
        )
        article = result.scalar_one_or_none()
        
        if not article:
            print(f"Article {article_id} not found")
            return False
        
        # Stage 1: FETCH
        article.status = ArticleStatus.FETCHING
        await db.commit()
        
        html = await fetch_article(article.url)
        if not html:
            article.status = ArticleStatus.FAILED
            article.error_message = "Failed to fetch article"
            await db.commit()
            return False
        
        article.raw_html = html
        
        # Stage 2: PARSE
        article.status = ArticleStatus.PARSING
        await db.commit()
        
        parsed = await parse_article(html)
        if not parsed:
            article.status = ArticleStatus.FAILED
            article.error_message = "Failed to parse article"
            await db.commit()
            return False
        
        article.title = parsed["title"]
        article.parsed_text = parsed["text"]
        article.word_count = parsed["word_count"]
        
        # Stage 3: CHUNK
        article.status = ArticleStatus.CHUNKING
        await db.commit()
        
        chunks = await chunk_article(parsed["text"])
        article.chunk_count = len(chunks)
        
        # Stage 4: SUMMARIZE
        article.status = ArticleStatus.SUMMARIZING
        await db.commit()
        
        summary = await summarize_article(chunks, parsed["title"])
        article.summary = summary
        
        # Stage 5: RENDER
        article.status = ArticleStatus.RENDERING
        await db.commit()
        
        rendered = await render_article(summary, format="text")
        
        # Mark as completed
        article.status = ArticleStatus.COMPLETED
        article.completed_at = datetime.utcnow()
        await db.commit()
        
        print(f"✅ Article {article_id} processed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error processing article {article_id}: {e}")
        # Only update article status if it was loaded successfully
        if article is not None:
            try:
                article.status = ArticleStatus.FAILED
                article.error_message = str(e)
                await db.commit()
            except Exception as commit_error:
                print(f"❌ Failed to update article status: {commit_error}")
                await db.rollback()
        return False
