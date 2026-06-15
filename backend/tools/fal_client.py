import logging
import os

import fal_client

from config import settings

log = logging.getLogger(__name__)


async def generate_visual(company_name: str, summary: str) -> dict | None:
    """
    Generate an abstract visual representation of the company using fal.ai.
    Circuit-broken: returns None on empty key, network timeout, or any exception.
    """
    if not settings.fal_key:
        log.warning("FAL_KEY is empty or not set. Skipping visual generation.")
        return None

    # Sync FAL_KEY to os.environ so fal_client uses it automatically
    os.environ["FAL_KEY"] = settings.fal_key

    prompt = f"Abstract visualization representing {company_name}: {summary[:200]}. Modern, clean, corporate style."
    log.info(f"Triggering fal visual generation for {company_name}...")

    try:
        # fal-client subscribe_async supports client_timeout to limit queue + processing time
        result = await fal_client.subscribe_async(
            "fal-ai/flux/schnell",
            arguments={
                "prompt": prompt,
                "image_size": "landscape_16_9",
            },
            client_timeout=30.0,
        )

        if result and "images" in result and len(result["images"]) > 0:
            image_url = result["images"][0].get("url")
            if image_url:
                return {"image_url": image_url, "prompt": prompt}

        log.error(f"fal API returned unexpected structure: {result}")
        return None
    except Exception as e:
        log.error(f"Failed to generate visual via fal for {company_name}: {e}")
        return None
