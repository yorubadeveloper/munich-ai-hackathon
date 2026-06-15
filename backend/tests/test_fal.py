from unittest.mock import AsyncMock, patch

import pytest

from config import settings
from tools import fal_client


@pytest.mark.asyncio
async def test_generate_visual_no_key():
    with patch.object(settings, "fal_key", ""):
        result = await fal_client.generate_visual("Acme Corp", "A cool AI startup")
        assert result is None


@pytest.mark.asyncio
async def test_generate_visual_success():
    mock_response = {"images": [{"url": "https://fal.media/files/monkey/some_hash.png"}]}
    with patch.object(settings, "fal_key", "test-key-123"):
        with patch("fal_client.subscribe_async", new_callable=AsyncMock) as mock_subscribe:
            mock_subscribe.return_value = mock_response
            result = await fal_client.generate_visual("Acme Corp", "A cool AI startup")

            assert result is not None
            assert result["image_url"] == "https://fal.media/files/monkey/some_hash.png"
            assert "Acme Corp" in result["prompt"]
            mock_subscribe.assert_called_once()


@pytest.mark.asyncio
async def test_generate_visual_timeout():
    with patch.object(settings, "fal_key", "test-key-123"):
        with patch("fal_client.subscribe_async", new_callable=AsyncMock) as mock_subscribe:
            mock_subscribe.side_effect = Exception("API connection timeout")
            result = await fal_client.generate_visual("Acme Corp", "A cool AI startup")

            assert result is None
            mock_subscribe.assert_called_once()
