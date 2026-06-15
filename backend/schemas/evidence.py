from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ResourceName(str, Enum):
    TAVILY = "Tavily"
    PIONEER = "Pioneer"
    GEMINI = "Gemini"
    TELEGRAM = "Telegram"
    FAL = "fal"


class ArtifactType(str, Enum):
    SOURCE = "source"
    ENTITY_EXTRACTION = "entity_extraction"
    REASONING = "reasoning"
    APPROVAL_STATE = "approval_state"
    VISUAL_ARTIFACT = "visual_artifact"
    PIONEER_EVAL = "pioneer_eval"


class EvidenceEventBase(BaseModel):
    resource_name: ResourceName
    artifact_type: ArtifactType
    payload: Dict[str, Any] = Field(default_factory=dict)
    status: str = Field(default="success")
    error_context: Optional[Dict[str, Any]] = None


class EvidenceEventCreate(EvidenceEventBase):
    company_id: UUID


class EvidenceEventResponse(EvidenceEventBase):
    id: UUID
    company_id: UUID
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)
