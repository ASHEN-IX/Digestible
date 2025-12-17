"""
Stage 4: SUMMARIZE - Generate summary from chunks
Phase 0: Placeholder implementation
"""

from typing import List


async def summarize_article(chunks: List[str], title: str) -> str:
    """
    Generate summary from article chunks

    Args:
        chunks: List of text chunks
        title: Article title

    Returns:
        Summary text
    """
    # Phase 0: Simple placeholder
    # Phase 1+: Integrate AI model (OpenAI, Claude, etc.)

    total_words = sum(len(chunk.split()) for chunk in chunks)

    summary = f"""
    [PLACEHOLDER SUMMARY]
    
    Title: {title}
    Chunks processed: {len(chunks)}
    Total words: {total_words}
    
    This is a placeholder summary. In Phase 1, this will be replaced with 
    AI-generated summaries using LLMs.
    
    Key points will be extracted and formatted as:
    • Point 1
    • Point 2
    • Point 3
    """

    return summary.strip()
