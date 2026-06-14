import asyncio
from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from agents.orchestrator import run_pipeline
from database import get_db
from models import Company, EvidenceEvent, Message, Research
from schemas.dossier import ApprovalActionResponse, ApprovalState, CompanyDossierResponse
from tools.telegram_client import send_dashboard_receipt

router = APIRouter()


@router.get("/companies/{company_id}/dossier", response_model=CompanyDossierResponse)
async def get_company_dossier(company_id: UUID, db: AsyncSession = Depends(get_db)):
    # 1. Fetch Company
    company = await db.get(Company, company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    # 2. Fetch Research
    research_result = await db.execute(select(Research).where(Research.company_id == company_id))
    research = research_result.scalar_one_or_none()

    # 3. Fetch Evidence Events
    events_result = await db.execute(
        select(EvidenceEvent).where(EvidenceEvent.company_id == company_id).order_by(EvidenceEvent.timestamp.asc())
    )
    evidence_events = list(events_result.scalars().all())

    # 4. Fetch Outreach Draft (Message)
    # Get the latest message to find the outreach hook and maybe approval state
    message_result = await db.execute(
        select(Message).where(Message.company_id == company_id).order_by(Message.id.desc()).limit(1)
    )
    message = message_result.scalar_one_or_none()

    outreach_hook: Optional[str] = None
    if message:
        outreach_hook = message.draft_body or message.final_body

    # 5. Determine Approval State
    # We can infer this from evidence events (ResourceName.TELEGRAM, ArtifactType.APPROVAL_STATE)
    # or from the Message model. Let's look at Telegram evidence events first as it's more specific to S01/S02 logic
    approval_status = "pending"
    approval_comment: Optional[str] = None
    approval_updated_at: Optional[datetime] = None

    for event in reversed(evidence_events):
        if event.resource_name == "Telegram" and event.artifact_type == "approval_state":
            payload = event.payload or {}
            is_approved = payload.get("approved")
            if is_approved is True:
                approval_status = "approved"
            elif is_approved is False:
                approval_status = "rejected"
            else:
                approval_status = "pending"

            approval_comment = payload.get("comment")
            approval_updated_at = event.timestamp
            break

    # Fallback to message status if no event found
    if approval_status == "pending" and not approval_updated_at and message:
        if message.status == "approved" or message.approved_at:
            approval_status = "approved"
            approval_updated_at = message.approved_at
        elif message.status == "rejected":
            approval_status = "rejected"

    approval_state = ApprovalState(status=approval_status, comment=approval_comment, updated_at=approval_updated_at)

    # 6. Construct Dossier
    return CompanyDossierResponse(
        id=company.id,
        name=company.name,
        website=company.website,
        job_url=company.job_url,
        status=company.status,
        fit_score=company.fit_score,
        discovered_at=company.discovered_at,
        funding_stage=research.funding_stage if research else None,
        tech_stack=research.tech_stack if research else [],
        hiring_manager=research.hiring_manager_name if research else None,
        hiring_manager_role=research.hiring_manager_role if research else None,
        hiring_manager_linkedin=research.hiring_manager_linkedin if research else None,
        recent_news=research.recent_news if research else None,
        fit_reasoning=research.fit_reasoning if research else None,
        evidence_events=evidence_events,
        outreach_hook=outreach_hook,
        approval_state=approval_state,
    )


@router.patch("/companies/{company_id}/approve", response_model=ApprovalActionResponse)
async def approve_company(company_id: UUID, db: AsyncSession = Depends(get_db)):
    company = await db.get(Company, company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    # Update company status
    company.status = "approved"

    # Also update any pending message to approved
    msg_result = await db.execute(select(Message).where(Message.company_id == company.id, Message.status == "pending"))
    message = msg_result.scalar_one_or_none()
    if message:
        message.status = "approved"

    # Create evidence event
    event = EvidenceEvent(
        company_id=company.id,
        resource_name="Telegram",
        artifact_type="approval_state",
        payload={"approved": True, "source": "dashboard"},
        status="success",
        timestamp=datetime.utcnow(),
    )
    db.add(event)
    await db.commit()

    # Send receipt notification to Telegram bot (asynchronously, ignoring errors)
    asyncio.create_task(send_dashboard_receipt(company.name, "approve"))

    # Spawn orchestrator pipeline update
    asyncio.create_task(run_pipeline(str(company.id)))

    return ApprovalActionResponse(status="approved", company_id=company.id)


@router.patch("/companies/{company_id}/reject", response_model=ApprovalActionResponse)
async def reject_company(company_id: UUID, db: AsyncSession = Depends(get_db)):
    company = await db.get(Company, company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    # Update company status
    company.status = "rejected"

    # Also update any pending message to rejected
    msg_result = await db.execute(select(Message).where(Message.company_id == company.id, Message.status == "pending"))
    message = msg_result.scalar_one_or_none()
    if message:
        message.status = "rejected"

    # Create evidence event
    event = EvidenceEvent(
        company_id=company.id,
        resource_name="Telegram",
        artifact_type="approval_state",
        payload={"approved": False, "source": "dashboard"},
        status="success",
        timestamp=datetime.utcnow(),
    )
    db.add(event)
    await db.commit()

    # Send receipt notification to Telegram bot (asynchronously, ignoring errors)
    asyncio.create_task(send_dashboard_receipt(company.name, "reject"))

    return ApprovalActionResponse(status="rejected", company_id=company.id)
