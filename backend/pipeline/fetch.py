"""
Stage 1: FETCH - Download HTML content from URL
"""

from typing import Optional

import httpx

from backend.config import get_settings

settings = get_settings()


async def fetch_article(url: str) -> Optional[str]:
    """
    Fetch HTML content from a URL

    Args:
        url: The URL to fetch

    Returns:
        HTML content as string, or None if failed
    """
    try:
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            response = await client.get(url)
            response.raise_for_status()

            # Check content type
            content_type = response.headers.get("content-type", "")
            if "text/html" not in content_type:
                raise ValueError(f"Invalid content type: {content_type}")

            # Check content length
            html = response.text
            if len(html) > settings.max_content_length:
                raise ValueError(f"Content too large: {len(html)} bytes")

            return html

    except httpx.HTTPError as e:
        print(f"HTTP error fetching {url}: {e}")
        return None
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None
