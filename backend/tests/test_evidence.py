import uuid
from datetime import datetime

import pytest
from pydantic import ValidationError

from schemas.evidence import (
    ArtifactType,
    EvidenceEventCreate,
    EvidenceEventResponse,
    ResourceName,
)


def test_evidence_event_create_valid():
    event = EvidenceEventCreate(
        company_id=uuid.uuid4(),
        resource_name=ResourceName.TAVILY,
        artifact_type=ArtifactType.SOURCE,
        payload={"key": "value"},
    )
    assert event.resource_name == ResourceName.TAVILY
    assert event.artifact_type == ArtifactType.SOURCE
    assert event.payload == {"key": "value"}
    assert event.status == "success"
    assert event.error_context is None


def test_evidence_event_create_invalid_resource():
    with pytest.raises(ValidationError):
        EvidenceEventCreate(
            company_id=uuid.uuid4(), resource_name="InvalidResource", artifact_type=ArtifactType.SOURCE, payload={}
        )


def test_evidence_event_create_invalid_artifact():
    with pytest.raises(ValidationError):
        EvidenceEventCreate(
            company_id=uuid.uuid4(), resource_name=ResourceName.TAVILY, artifact_type="invalid_artifact", payload={}
        )


def test_evidence_event_response_from_orm(company_uuid):
    # Mocking an ORM object
    class MockORM:
        def __init__(self):
            self.id = uuid.uuid4()
            self.company_id = company_uuid
            self.resource_name = "Tavily"
            self.artifact_type = "source"
            self.payload = {"data": 123}
            self.status = "success"
            self.timestamp = datetime.utcnow()
            self.error_context = None

    orm_obj = MockORM()
    response = EvidenceEventResponse.model_validate(orm_obj)

    assert response.id == orm_obj.id
    assert response.company_id == orm_obj.company_id
    assert response.resource_name == ResourceName.TAVILY
    assert response.artifact_type == ArtifactType.SOURCE


def test_fixtures_load_correctly(
    tavily_evidence, pioneer_evidence, gemini_evidence, telegram_evidence, fal_evidence, partial_failure_evidence
):
    assert tavily_evidence.resource_name == ResourceName.TAVILY
    assert pioneer_evidence.resource_name == ResourceName.PIONEER
    assert gemini_evidence.resource_name == ResourceName.GEMINI
    assert telegram_evidence.resource_name == ResourceName.TELEGRAM
    assert fal_evidence.resource_name == ResourceName.FAL

    assert partial_failure_evidence.status == "error"
    assert partial_failure_evidence.error_context is not None
    assert partial_failure_evidence.error_context["code"] == "timeout"
