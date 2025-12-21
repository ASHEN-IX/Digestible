"""
Stage 3: CHUNK - Split article into processable segments
"""

from typing import List

from backend.config import get_settings

settings = get_settings()


def chunk_article(text: str) -> List[str]:
    """
    Split article text into chunks for processing

    Args:
        text: Parsed article text

    Returns:
        List of text chunks
    """
    # Simple sentence-based chunking
    # In production, use more sophisticated NLP chunking

    sentences = text.split(". ")
    chunks = []
    current_chunk = ""

    for sentence in sentences:
        # Add sentence to current chunk if it fits
        if len(current_chunk) + len(sentence) < settings.chunk_size:
            current_chunk += sentence + ". "
        else:
            # Save current chunk and start new one
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = sentence + ". "

            # Safety limit
            if len(chunks) >= settings.max_chunks:
                break

    # Add final chunk
    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks
