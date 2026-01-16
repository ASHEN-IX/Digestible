"""
Pipeline Orchestrator - Coordinates all pipeline stages
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.database.models import Article, ArticleStatus
from backend.tts import generate_article_audio

from .chunk import chunk_article
from .fetch import fetch_article
from .parse import parse_article
from .render import render_article
from .summarize import summarize_article


def process_article_pipeline(url: str, article_id: str = None) -> dict:
    """
    Process an article through the complete pipeline (without database operations)

    Args:
        url: Article URL to process
        article_id: Optional article ID for audio file naming

    Returns:
        Dictionary with processed article data
    """
    try:
        # Stage 1: FETCH
        html = fetch_article(url)
        if not html:
            raise ValueError("Failed to fetch article")

        # Stage 2: PARSE
        parsed = parse_article(html)
        if not parsed:
            raise ValueError("Failed to parse article")

        # Stage 3: CHUNK
        chunks = chunk_article(parsed["text"])

        # Stage 4: SUMMARIZE
        summary = summarize_article(chunks, parsed["title"])

        # Stage 5: GENERATE AUDIO
        audio_path = None
        if article_id:
            try:
                audio_path = generate_article_audio(article_id, summary)
            except Exception as e:
                print(f"⚠️  Audio generation failed, continuing without audio: {e}")

        # Stage 6: RENDER
        render_article(summary, format="text")

        return {
            "title": parsed["title"],
            "content": parsed["text"],
            "summary": summary,
            "audio_path": audio_path,
            "chunks_count": len(chunks),
            "word_count": parsed["word_count"],
            "raw_html": html,
        }

    except Exception as e:
        print(f"❌ Error processing article {url}: {e}")
        raise
