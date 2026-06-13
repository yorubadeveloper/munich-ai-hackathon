"""
Tavily search client.
Tavily's SDK is synchronous, so we run it in a thread to avoid blocking the
asyncio event loop.
"""
import asyncio
import logging

from tavily import TavilyClient

from config import settings

log = logging.getLogger(__name__)

client = TavilyClient(api_key=settings.tavily_api_key)


async def search(query: str, max_results: int = 5) -> list[dict]:
    def _search() -> list[dict]:
        try:
            response = client.search(
                query=query,
                max_results=max_results,
                search_depth="advanced",
                include_raw_content=True,
            )
            return response.get("results", [])
        except Exception as e:
            log.warning(f"Tavily search failed for '{query[:60]}': {e}")
            return []

    return await asyncio.to_thread(_search)
