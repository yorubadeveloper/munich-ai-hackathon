from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from schemas.evidence import EvidenceEventResponse


class ApprovalState(BaseModel):
    status: str  # e.g., "pending", "approved", "rejected"
    comment: Optional[str] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class CompanyDossierResponse(BaseModel):
    id: UUID
    name: str
    website: Optional[str] = None
    job_url: Optional[str] = None
    status: str
    fit_score: Optional[float] = None
    discovered_at: datetime

    # Research data
    funding_stage: Optional[str] = None
    tech_stack: List[str] = []
    hiring_manager: Optional[str] = None
    hiring_manager_role: Optional[str] = None
    hiring_manager_linkedin: Optional[str] = None
    recent_news: Optional[str] = None
    fit_reasoning: Optional[str] = None

    # Evidence and Outreach
    evidence_events: List[EvidenceEventResponse]
    outreach_hook: Optional[str] = None

    approval_state: ApprovalState

    model_config = ConfigDict(from_attributes=True)
