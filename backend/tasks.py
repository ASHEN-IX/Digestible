"""
Async tasks for article processing
"""

from backend.celery_app import celery_app
from backend.database.connection import SessionLocal
from backend.database.models import Article, ArticleStatus
from backend.pipeline.orchestrator import process_article_pipeline


@celery_app.task(bind=True, name="process_article")
def process_article_task(self, article_id: int):
    """
    Async task to process an article through the full pipeline

    Args:
        article_id: Database ID of the article to process
    """
    try:
        # Update status to processing
        with SessionLocal() as db:
            article = db.query(Article).filter(Article.id == article_id).first()
            if not article:
                raise ValueError(f"Article {article_id} not found")

            article.status = ArticleStatus.FETCHING
            article_url = article.url  # Store URL before session closes
            db.commit()

        # Process the article
        result = process_article_pipeline(article_url, article_id)

        # Update article with results
        with SessionLocal() as db:
            article = db.query(Article).filter(Article.id == article_id).first()
            if article:
                article.title = result.get("title", "")
                article.content = result.get("content", "")
                article.summary = result.get("summary", "")
                article.audio_path = result.get("audio_path")
                article.status = ArticleStatus.COMPLETED
                article.chunks_count = result.get("chunks_count", 0)
                article.word_count = result.get("word_count", 0)
                db.commit()

        return {"status": "success", "article_id": article_id}

    except Exception as e:
        # Update status to failed
        with SessionLocal() as db:
            article = db.query(Article).filter(Article.id == article_id).first()
            if article:
                article.status = ArticleStatus.FAILED
                article.error_message = str(e)
                db.commit()

        raise self.retry(countdown=60, max_retries=3, exc=e) from e
