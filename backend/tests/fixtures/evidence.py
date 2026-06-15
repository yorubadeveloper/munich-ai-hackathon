import uuid
from datetime import datetime, timezone

import pytest

from schemas.evidence import ArtifactType, EvidenceEventResponse, ResourceName


@pytest.fixture
def company_uuid():
    return uuid.uuid4()


@pytest.fixture
def tavily_evidence(company_uuid):
    return EvidenceEventResponse(
        id=uuid.uuid4(),
        company_id=company_uuid,
        timestamp=datetime.now(timezone.utc),
        resource_name=ResourceName.TAVILY,
        artifact_type=ArtifactType.SOURCE,
        payload={"url": "https://example.com/about", "snippet": "We are a series B startup..."},
        status="success",
    )


@pytest.fixture
def pioneer_evidence(company_uuid):
    return EvidenceEventResponse(
        id=uuid.uuid4(),
        company_id=company_uuid,
        timestamp=datetime.now(timezone.utc),
        resource_name=ResourceName.PIONEER,
        artifact_type=ArtifactType.ENTITY_EXTRACTION,
        payload={"entities": {"tech_stack": ["Python", "React", "PostgreSQL"], "headcount": "50-100"}},
        status="success",
    )


@pytest.fixture
def gemini_evidence(company_uuid):
    return EvidenceEventResponse(
        id=uuid.uuid4(),
        company_id=company_uuid,
        timestamp=datetime.now(timezone.utc),
        resource_name=ResourceName.GEMINI,
        artifact_type=ArtifactType.REASONING,
        payload={"reasoning": "Strong match due to overlapping tech stack and stage.", "score": 0.85},
        status="success",
    )


@pytest.fixture
def telegram_evidence(company_uuid):
    return EvidenceEventResponse(
        id=uuid.uuid4(),
        company_id=company_uuid,
        timestamp=datetime.now(timezone.utc),
        resource_name=ResourceName.TELEGRAM,
        artifact_type=ArtifactType.APPROVAL_STATE,
        payload={"approved": True, "comment": "Looks good, send it."},
        status="success",
    )


@pytest.fixture
def fal_evidence(company_uuid):
    return EvidenceEventResponse(
        id=uuid.uuid4(),
        company_id=company_uuid,
        timestamp=datetime.now(timezone.utc),
        resource_name=ResourceName.FAL,
        artifact_type=ArtifactType.VISUAL_ARTIFACT,
        payload={"image_url": "https://fal.ai/example.png", "prompt": "Visualization of company tech stack"},
        status="success",
    )


@pytest.fixture
def partial_failure_evidence(company_uuid):
    return EvidenceEventResponse(
        id=uuid.uuid4(),
        company_id=company_uuid,
        timestamp=datetime.now(timezone.utc),
        resource_name=ResourceName.PIONEER,
        artifact_type=ArtifactType.ENTITY_EXTRACTION,
        payload={},
        status="error",
        error_context={"error_message": "Timeout while extracting entities", "code": "timeout"},
    )
