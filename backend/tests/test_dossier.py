import pytest
from fastapi import FastAPI
from httpx import AsyncClient

from models import Company, EvidenceEvent, Message, Research


@pytest.fixture
def app_with_routes():
    from main import app
    return app

@pytest.mark.anyio
async def test_get_dossier_success(app_with_routes: FastAPI, mocker, company_uuid, tavily_evidence, pioneer_evidence, gemini_evidence, telegram_evidence, partial_failure_evidence):
    from httpx import ASGITransport

    from database import get_db

    # Mock DB Session
    mock_db = mocker.AsyncMock()

    from datetime import datetime

    # Mock Company
    mock_company = Company(
        id=company_uuid,
        name="Test Company",
        website="https://test.example.com",
        status="approved",
        fit_score=0.85,
        discovered_at=datetime.utcnow()
    )
    mock_db.get.return_value = mock_company

    # Mock Research
    mock_research = Research(
        company_id=company_uuid,
        funding_stage="Series B",
        tech_stack=["Python", "React", "PostgreSQL"],
        fit_reasoning="Strong match due to overlapping tech stack and stage."
    )

    # Mock Evidence Events
    mock_events = []
    for ev in [tavily_evidence, pioneer_evidence, gemini_evidence, telegram_evidence, partial_failure_evidence]:
        event_model = EvidenceEvent(
            id=ev.id,
            company_id=ev.company_id,
            resource_name=ev.resource_name,
            artifact_type=ev.artifact_type,
            payload=ev.payload,
            status=ev.status,
            error_context=ev.error_context,
            timestamp=ev.timestamp
        )
        mock_events.append(event_model)

    # Mock Message
    mock_message = Message(
        company_id=company_uuid,
        channel="email",
        draft_body="Hey! Saw your startup...",
        status="approved"
    )

    async def mock_execute(query):
        mock_result = mocker.MagicMock()
        query_str = str(query).lower()
        if "research" in query_str:
            mock_result.scalar_one_or_none.return_value = mock_research
        elif "evidence_events" in query_str:
            mock_result.scalars().all.return_value = mock_events
        elif "messages" in query_str:
            mock_result.scalar_one_or_none.return_value = mock_message
        return mock_result

    mock_db.execute = mock_execute

    async def override_get_db():
        yield mock_db

    app_with_routes.dependency_overrides[get_db] = override_get_db

    try:
        async with AsyncClient(transport=ASGITransport(app=app_with_routes), base_url="http://test/") as client:
            response = await client.get(f"/api/companies/{company_uuid}/dossier")

        assert response.status_code == 200
        data = response.json()

        assert data["id"] == str(company_uuid)
        assert data["name"] == "Test Company"
        assert data["funding_stage"] == "Series B"
        assert "Python" in data["tech_stack"]
        assert data["outreach_hook"] == "Hey! Saw your startup..."
        assert data["approval_state"]["status"] == "approved"

        resources = [e["resource_name"] for e in data["evidence_events"]]
        assert "Tavily" in resources
        assert "Pioneer" in resources

        failures = [e for e in data["evidence_events"] if e["status"] == "error"]
        assert len(failures) == 1
        assert failures[0]["error_context"]["code"] == "timeout"
    finally:
        app_with_routes.dependency_overrides.clear()

@pytest.mark.anyio
async def test_get_dossier_not_found(app_with_routes: FastAPI, mocker):
    import uuid

    from httpx import ASGITransport

    from database import get_db

    random_id = uuid.uuid4()

    mock_db = mocker.AsyncMock()
    mock_db.get.return_value = None

    async def override_get_db():
        yield mock_db

    app_with_routes.dependency_overrides[get_db] = override_get_db

    try:
        async with AsyncClient(transport=ASGITransport(app=app_with_routes), base_url="http://test/") as client:
            response = await client.get(f"/api/companies/{random_id}/dossier")

        assert response.status_code == 404
    finally:
        app_with_routes.dependency_overrides.clear()
