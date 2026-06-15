pytest_plugins = ("pytest_asyncio",)
import pytest
from fastapi import FastAPI
from httpx import AsyncClient

from models import Company, EvidenceEvent, Message, Research


@pytest.fixture
def app_with_routes():
    from main import app

    return app


@pytest.mark.anyio
async def test_get_dossier_success(
    app_with_routes: FastAPI,
    mocker,
    company_uuid,
    tavily_evidence,
    pioneer_evidence,
    gemini_evidence,
    telegram_evidence,
    fal_evidence,
    partial_failure_evidence,
):
    from httpx import ASGITransport

    from database import get_db

    # Mock DB Session
    mock_db = mocker.AsyncMock()
    mock_db.add = mocker.MagicMock()

    from datetime import datetime

    # Mock Company
    mock_company = Company(
        id=company_uuid,
        name="Test Company",
        website="https://test.example.com",
        status="approved",
        fit_score=0.85,
        discovered_at=datetime.utcnow(),
    )
    mock_db.get.return_value = mock_company

    # Mock Research
    mock_research = Research(
        company_id=company_uuid,
        funding_stage="Series B",
        tech_stack=["Python", "React", "PostgreSQL"],
        fit_reasoning="Strong match due to overlapping tech stack and stage.",
    )

    # Mock Evidence Events
    mock_events = []
    for ev in [
        tavily_evidence,
        pioneer_evidence,
        gemini_evidence,
        telegram_evidence,
        fal_evidence,
        partial_failure_evidence,
    ]:
        event_model = EvidenceEvent(
            id=ev.id,
            company_id=ev.company_id,
            resource_name=ev.resource_name,
            artifact_type=ev.artifact_type,
            payload=ev.payload,
            status=ev.status,
            error_context=ev.error_context,
            timestamp=ev.timestamp,
        )
        mock_events.append(event_model)

    # Mock Message
    mock_message = Message(
        company_id=company_uuid, channel="email", draft_body="Hey! Saw your startup...", status="approved"
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
        assert any(
            e["resource_name"] == "fal" and e["artifact_type"] == "visual_artifact" for e in data["evidence_events"]
        )

        failures = [e for e in data["evidence_events"] if e["status"] == "error"]
        assert len(failures) == 1
        assert failures[0]["error_context"]["code"] == "timeout"
    finally:
        app_with_routes.dependency_overrides.clear()


@pytest.mark.anyio
async def test_get_dossier_partial_failures_only(
    app_with_routes: FastAPI,
    mocker,
    company_uuid,
    partial_failure_evidence,
):
    from httpx import ASGITransport

    from database import get_db

    # Mock DB Session
    mock_db = mocker.AsyncMock()
    mock_db.add = mocker.MagicMock()

    from datetime import datetime

    # Mock Company
    mock_company = Company(
        id=company_uuid,
        name="Test Company",
        website="https://test.example.com",
        status="approved",
        fit_score=0.85,
        discovered_at=datetime.utcnow(),
    )
    mock_db.get.return_value = mock_company

    # Mock Research
    mock_research = Research(
        company_id=company_uuid,
        funding_stage="Series B",
        tech_stack=["Python", "React", "PostgreSQL"],
        fit_reasoning="Strong match due to overlapping tech stack and stage.",
    )

    # Mock Evidence Events
    event_model = EvidenceEvent(
        id=partial_failure_evidence.id,
        company_id=partial_failure_evidence.company_id,
        resource_name=partial_failure_evidence.resource_name,
        artifact_type=partial_failure_evidence.artifact_type,
        payload=partial_failure_evidence.payload,
        status=partial_failure_evidence.status,
        error_context=partial_failure_evidence.error_context,
        timestamp=partial_failure_evidence.timestamp,
    )
    mock_events = [event_model]

    # Mock Message
    mock_message = Message(
        company_id=company_uuid, channel="email", draft_body="Hey! Saw your startup...", status="approved"
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

        # Evidence events should only contain the partial failure
        events = data["evidence_events"]
        assert len(events) == 1
        assert events[0]["status"] == "error"
        assert events[0]["error_context"]["code"] == "timeout"

        # Verify no success events are present
        successes = [e for e in events if e["status"] == "success"]
        assert len(successes) == 0
    finally:
        app_with_routes.dependency_overrides.clear()


@pytest.mark.anyio
async def test_get_dossier_not_found(app_with_routes: FastAPI, mocker):
    import uuid

    from httpx import ASGITransport

    from database import get_db

    random_id = uuid.uuid4()

    mock_db = mocker.AsyncMock()
    mock_db.add = mocker.MagicMock()
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


@pytest.mark.anyio
async def test_approve_company_success(app_with_routes: FastAPI, mocker, company_uuid):
    from httpx import ASGITransport

    from database import get_db

    # Mock database session
    mock_db = mocker.AsyncMock()
    mock_db.add = mocker.MagicMock()
    mock_company = Company(
        id=company_uuid, name="Approve Test Corp", website="https://approve.example.com", status="discovered"
    )
    mock_db.get.return_value = mock_company

    # Mock Message query
    mock_msg = Message(id=company_uuid, company_id=company_uuid, status="pending")
    mock_result = mocker.MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_msg
    mock_db.execute.return_value = mock_result

    # Mock external handlers to prevent background execution in tests
    mock_send_receipt = mocker.patch("api.dossier.send_dashboard_receipt")
    mock_run_pipeline = mocker.patch("api.dossier.run_pipeline")

    async def override_get_db():
        yield mock_db

    app_with_routes.dependency_overrides[get_db] = override_get_db

    try:
        async with AsyncClient(transport=ASGITransport(app=app_with_routes), base_url="http://test/") as client:
            response = await client.patch(f"/api/companies/{company_uuid}/approve")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "approved"
        assert data["company_id"] == str(company_uuid)

        # Verify status updates on company and message
        assert mock_company.status == "approved"
        assert mock_msg.status == "approved"

        # Verify EvidenceEvent was added
        mock_db.add.assert_called_once()
        event_added = mock_db.add.call_args[0][0]
        assert event_added.resource_name == "Telegram"
        assert event_added.artifact_type == "approval_state"
        assert event_added.payload == {"approved": True, "source": "dashboard"}

        # Verify mock calls
        mock_send_receipt.assert_called_once_with("Approve Test Corp", "approve")
        mock_run_pipeline.assert_called_once_with(str(company_uuid))
    finally:
        app_with_routes.dependency_overrides.clear()


@pytest.mark.anyio
async def test_reject_company_success(app_with_routes: FastAPI, mocker, company_uuid):
    from httpx import ASGITransport

    from database import get_db

    # Mock database session
    mock_db = mocker.AsyncMock()
    mock_db.add = mocker.MagicMock()
    mock_company = Company(
        id=company_uuid, name="Reject Test Corp", website="https://reject.example.com", status="discovered"
    )
    mock_db.get.return_value = mock_company

    # Mock Message query
    mock_msg = Message(id=company_uuid, company_id=company_uuid, status="pending")
    mock_result = mocker.MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_msg
    mock_db.execute.return_value = mock_result

    mock_send_receipt = mocker.patch("api.dossier.send_dashboard_receipt")
    mock_run_pipeline = mocker.patch("api.dossier.run_pipeline")

    async def override_get_db():
        yield mock_db

    app_with_routes.dependency_overrides[get_db] = override_get_db

    try:
        async with AsyncClient(transport=ASGITransport(app=app_with_routes), base_url="http://test/") as client:
            response = await client.patch(f"/api/companies/{company_uuid}/reject")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "rejected"
        assert data["company_id"] == str(company_uuid)

        # Verify status updates on company and message
        assert mock_company.status == "rejected"
        assert mock_msg.status == "rejected"

        # Verify EvidenceEvent was added
        mock_db.add.assert_called_once()
        event_added = mock_db.add.call_args[0][0]
        assert event_added.resource_name == "Telegram"
        assert event_added.artifact_type == "approval_state"
        assert event_added.payload == {"approved": False, "source": "dashboard"}

        # Verify mock calls
        mock_send_receipt.assert_called_once_with("Reject Test Corp", "reject")
        mock_run_pipeline.assert_not_called()
    finally:
        app_with_routes.dependency_overrides.clear()


@pytest.mark.anyio
async def test_approve_company_not_found(app_with_routes: FastAPI, mocker):
    import uuid

    from httpx import ASGITransport

    from database import get_db

    random_id = uuid.uuid4()
    mock_db = mocker.AsyncMock()
    mock_db.add = mocker.MagicMock()
    mock_db.get.return_value = None

    async def override_get_db():
        yield mock_db

    app_with_routes.dependency_overrides[get_db] = override_get_db

    try:
        async with AsyncClient(transport=ASGITransport(app=app_with_routes), base_url="http://test/") as client:
            response = await client.patch(f"/api/companies/{random_id}/approve")

        assert response.status_code == 404
    finally:
        app_with_routes.dependency_overrides.clear()


@pytest.mark.anyio
async def test_reject_company_not_found(app_with_routes: FastAPI, mocker):
    import uuid

    from httpx import ASGITransport

    from database import get_db

    random_id = uuid.uuid4()
    mock_db = mocker.AsyncMock()
    mock_db.add = mocker.MagicMock()
    mock_db.get.return_value = None

    async def override_get_db():
        yield mock_db

    app_with_routes.dependency_overrides[get_db] = override_get_db

    try:
        async with AsyncClient(transport=ASGITransport(app=app_with_routes), base_url="http://test/") as client:
            response = await client.patch(f"/api/companies/{random_id}/reject")

        assert response.status_code == 404
    finally:
        app_with_routes.dependency_overrides.clear()
