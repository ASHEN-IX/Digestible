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
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/91.0.4472.124 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }

        async with httpx.AsyncClient(
            timeout=30.0, follow_redirects=True, headers=headers
        ) as client:
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
        print(f"Response status: {e.response.status_code if hasattr(e, 'response') else 'Unknown'}")
        return None
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None
