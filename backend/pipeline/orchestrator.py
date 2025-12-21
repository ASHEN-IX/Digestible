"""
Pipeline Orchestrator - Coordinates all pipeline stages
"""

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.database.models import Article, ArticleStatus

from .chunk import chunk_article
from .fetch import fetch_article
from .parse import parse_article
from .render import render_article
from .summarize import summarize_article


def process_article(article_id: str, db: Session) -> bool:
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
        result = db.execute(select(Article).where(Article.id == article_id))
        article = result.scalar_one_or_none()

        if not article:
            print(f"Article {article_id} not found")
            return False

        # Stage 1: FETCH
        article.status = ArticleStatus.FETCHING
        db.commit()

        html = fetch_article(article.url)
        if not html:
            article.status = ArticleStatus.FAILED
            article.error_message = "Failed to fetch article"
            db.commit()
            return False

        article.raw_html = html

        # Stage 2: PARSE
        article.status = ArticleStatus.PARSING
        db.commit()

        parsed = parse_article(html)
        if not parsed:
            article.status = ArticleStatus.FAILED
            article.error_message = "Failed to parse article"
            db.commit()
            return False

        article.title = parsed["title"]
        article.parsed_text = parsed["text"]
        article.word_count = parsed["word_count"]

        # Stage 3: CHUNK
        article.status = ArticleStatus.CHUNKING
        db.commit()

        chunks = chunk_article(parsed["text"])
        article.chunk_count = len(chunks)

        # Stage 4: SUMMARIZE
        article.status = ArticleStatus.SUMMARIZING
        db.commit()

        summary = summarize_article(chunks, parsed["title"])
        article.summary = summary

        # Stage 5: RENDER
        article.status = ArticleStatus.RENDERING
        db.commit()

        render_article(summary, format="text")

        # Mark as completed
        article.status = ArticleStatus.COMPLETED
        article.completed_at = datetime.utcnow()
        db.commit()

        print(f"✅ Article {article_id} processed successfully")
        return True

    except Exception as e:
        print(f"❌ Error processing article {article_id}: {e}")
        # Only update article status if it was loaded successfully
        if article is not None:
            try:
                article.status = ArticleStatus.FAILED
                article.error_message = str(e)
                db.commit()
            except Exception as commit_error:
                print(f"❌ Failed to update article status: {commit_error}")
                db.rollback()
        return False
