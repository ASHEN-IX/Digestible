"""
Stage 2: PARSE - Extract clean article text from HTML
"""

import re
from typing import Dict, Optional

from bs4 import BeautifulSoup


async def parse_article(html: str) -> Optional[Dict[str, str]]:
    """
    Parse HTML and extract article content

    Args:
        html: Raw HTML content

    Returns:
        Dict with 'title' and 'text', or None if failed
    """
    try:
        soup = BeautifulSoup(html, "html.parser")

        # Remove script and style elements
        for script in soup(["script", "style", "nav", "header", "footer"]):
            script.decompose()

        # Extract title
        title = None
        if soup.title:
            title = soup.title.string
        elif soup.find("h1"):
            title = soup.find("h1").get_text()

        # Extract main content
        # Try common article containers first
        article = None
        for selector in [
            "article",
            "main",
            "[role='main']",
            ".post-content",
            ".article-content",
        ]:
            article = soup.select_one(selector)
            if article:
                break

        # Fallback to body
        if not article:
            article = soup.find("body")

        if not article:
            return None

        # Get text and clean it
        text = article.get_text(separator="\n", strip=True)

        # Remove excessive whitespace
        text = re.sub(r"\n\s*\n", "\n\n", text)
        text = re.sub(r" +", " ", text)

        # Count words
        word_count = len(text.split())

        return {
            "title": title or "Untitled",
            "text": text,
            "word_count": word_count,
        }

    except Exception as e:
        print(f"Error parsing HTML: {e}")
        return None
