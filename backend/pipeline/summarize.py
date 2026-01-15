"""
Stage 4: SUMMARIZE - Generate summary from chunks
Phase 1: OpenRouter AI integration
"""

from typing import List

import requests

from backend.config import get_settings

settings = get_settings()


def summarize_article(chunks: List[str], title: str) -> str:
    """
    Generate summary from article chunks using OpenRouter AI

    Args:
        chunks: List of text chunks
        title: Article title

    Returns:
        AI-generated summary text
    """
    try:
        # Check if API key is configured
        if not settings.openrouter_api_key:
            raise ValueError("OpenRouter API key not configured")

        # Combine chunks into full text (limit to reasonable size)
        full_text = " ".join(chunks)
        if len(full_text) > 10000:  # Limit to 10k chars to avoid token limits
            full_text = full_text[:10000] + "..."

        # Create prompt for summarization
        prompt = (
            "Please provide a concise summary of the following article as a bullet-point list.\n"
            "Focus on the 5-7 most important points and key takeaways.\n"
            "Use clear, actionable bullets.\n\n"
            f"Title: {title}\n\n"
            f"Article content:\n{full_text}\n\n"
            "Summary (as bullet points):"
        )

        # Call OpenRouter API directly with requests
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {settings.openrouter_api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://digestible.app",
                "X-Title": "Digestible",
            },
            json={
                "model": "meta-llama/llama-3.2-3b-instruct:free",
                "messages": [{"role": "user", "content": prompt}],
            },
            timeout=60,
        )

        response.raise_for_status()
        result = response.json()

        summary = result["choices"][0]["message"]["content"].strip()

        # Add some metadata
        total_words = sum(len(chunk.split()) for chunk in chunks)
        metadata = f"\n\n📊 **Article Stats:** {len(chunks)} chunks, {total_words} words"

        return summary + metadata

    except Exception as e:
        # Fallback to placeholder if AI fails
        print(f"❌ OpenRouter API error: {e}")
        total_words = sum(len(chunk.split()) for chunk in chunks)

        return f"""
        [AI SUMMARY UNAVAILABLE]

        Title: {title}
        Chunks processed: {len(chunks)}
        Total words: {total_words}

        Unable to generate AI summary due to API error: {str(e)}

        Please check your OpenRouter API key and try again.
        """.strip()
