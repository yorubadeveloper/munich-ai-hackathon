pytest_plugins = ("pytest_asyncio",)
import uuid
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
async def test_generate_visual_failure():
    with patch.object(settings, "fal_key", "test-key-123"):
        with patch("fal_client.subscribe_async", new_callable=AsyncMock) as mock_subscribe:
            mock_subscribe.side_effect = Exception("API connection timeout")
            result = await fal_client.generate_visual("Acme Corp", "A cool AI startup")

            assert result is None
            mock_subscribe.assert_called_once()


@pytest.mark.asyncio
async def test_trigger_fal_generation_success(mocker):
    from agents.orchestrator import _trigger_fal_generation

    mock_session = mocker.AsyncMock()
    mock_session.add = mocker.MagicMock()
    # Mock AsyncSessionLocal to return our mock_session when used as an async context manager
    mock_session_local = mocker.patch("agents.orchestrator.AsyncSessionLocal")
    mock_session_local.return_value.__aenter__.return_value = mock_session

    mock_generate = mocker.patch("tools.fal_client.generate_visual", new_callable=AsyncMock)
    mock_generate.return_value = {"image_url": "https://fal.media/img.png", "prompt": "prompt"}

    company_id = uuid.uuid4()
    await _trigger_fal_generation(company_id, "Test Company", "recent news")

    mock_generate.assert_called_once_with("Test Company", "recent news")
    mock_session.add.assert_called_once()
    added_event = mock_session.add.call_args[0][0]
    assert added_event.company_id == company_id
    assert added_event.resource_name == "fal"
    assert added_event.artifact_type == "visual_artifact"
    assert added_event.status == "success"
    assert added_event.payload == {"image_url": "https://fal.media/img.png", "prompt": "prompt"}
    mock_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_trigger_fal_generation_failure(mocker):
    from agents.orchestrator import _trigger_fal_generation

    mock_session = mocker.AsyncMock()
    mock_session.add = mocker.MagicMock()
    mock_session_local = mocker.patch("agents.orchestrator.AsyncSessionLocal")
    mock_session_local.return_value.__aenter__.return_value = mock_session

    mock_generate = mocker.patch("tools.fal_client.generate_visual", new_callable=AsyncMock)
    mock_generate.side_effect = Exception("FAL API error")

    company_id = uuid.uuid4()
    await _trigger_fal_generation(company_id, "Test Company", "recent news")

    mock_generate.assert_called_once_with("Test Company", "recent news")
    mock_session.add.assert_called_once()
    added_event = mock_session.add.call_args[0][0]
    assert added_event.company_id == company_id
    assert added_event.resource_name == "fal"
    assert added_event.artifact_type == "visual_artifact"
    assert added_event.status == "error"
    assert "FAL API error" in added_event.error_context["reason"]
    mock_session.commit.assert_called_once()
