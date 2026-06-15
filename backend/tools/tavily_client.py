"""
Tavily search client.
Tavily's SDK is synchronous, so we run it in a thread to avoid blocking the
asyncio event loop.
"""

import asyncio
import logging

from tavily import TavilyClient

from config import settings
from tools.safe_http import UnsafeOutboundRequestError, validate_public_https_url

log = logging.getLogger(__name__)

client = TavilyClient(api_key=settings.tavily_api_key) if settings.tavily_api_key else None


def _normalize_search_query(query: str) -> str:
    normalized = (query or "").strip()
    lowered = normalized.lower()
    if lowered.startswith(("http://", "https://")):
        return validate_public_https_url(normalized)
    if "://" in normalized:
        raise UnsafeOutboundRequestError("Tavily URL queries must use http or https")
    return normalized


async def search(query: str, max_results: int = 5) -> list[dict]:
    if client is None:
        log.warning("TAVILY_API_KEY not set - skipping Tavily search.")
        return []
    try:
        safe_query = _normalize_search_query(query)
    except UnsafeOutboundRequestError as exc:
        log.warning(f"Rejected unsafe Tavily URL query: {exc}")
        return []

    def _search() -> list[dict]:
        try:
            response = client.search(
                query=safe_query,
                max_results=max_results,
                search_depth="advanced",
                include_raw_content=True,
            )
            return response.get("results", [])
        except Exception as e:
            log.warning(f"Tavily search failed for '{query[:60]}': {e}")
            return []

    return await asyncio.to_thread(_search)
