from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from agents.orchestrator import run_discovery, run_pipeline
from models import Company, Research, AgentLog
from database import AsyncSessionLocal
from tools.safe_http import UnsafeOutboundRequestError, normalize_public_https_url
import asyncio

router = APIRouter()


@router.post("/run")
async def trigger_run():
    asyncio.create_task(run_discovery())
    return {"status": "started"}


class AddCompanyIn(BaseModel):
    name: str
    company_url: str = ""
    job_url: str = ""
    job_description: str = ""


def _clean_public_url(url: str, field_name: str) -> str:
    try:
        return normalize_public_https_url(url)
    except UnsafeOutboundRequestError as exc:
        raise HTTPException(
            status_code=400,
            detail=f"{field_name} must be a public HTTPS URL: {exc}",
        ) from exc


@router.post("/companies/add")
async def add_company(data: AddCompanyIn):
    """
    Manually add a specific target company. Researches it (finds the
    decision-maker, enriches, scores fit) and drafts outreach, then sends it to
    the Telegram approval gate — same pipeline as auto-discovery.
    """
    name = data.name.strip()
    if not name:
        return {"status": "error", "detail": "name is required"}

    company_url = _clean_public_url(data.company_url, "company_url")
    job_url = _clean_public_url(data.job_url, "job_url")

    async with AsyncSessionLocal() as db:
        # Avoid duplicates by job_url if given, else by company_url, else by name.
        if job_url:
            existing = await db.execute(select(Company).where(Company.job_url == job_url))
        elif company_url:
            existing = await db.execute(select(Company).where(Company.website == company_url))
        else:
            existing = await db.execute(select(Company).where(Company.name == name))
        company = existing.scalar_one_or_none()

        if company:
            # Re-run it: clear prior research, reset status.
            old = await db.execute(
                select(Research).where(Research.company_id == company.id)
            )
            for r in old.scalars().all():
                await db.delete(r)
            company.status = "discovered"
            company.fit_score = None
            if company_url:
                company.website = company_url
            if job_url:
                company.job_url = job_url
            if data.job_description.strip():
                company.raw_job_text = data.job_description.strip()[:4000]
        else:
            company = Company(
                name=name,
                website=company_url or None,
                job_url=job_url or None,
                source="manual",
                raw_job_text=(data.job_description.strip() or None),
                status="discovered",
            )
            db.add(company)

        await db.commit()
        await db.refresh(company)

        db.add(
            AgentLog(
                agent="orchestrator",
                action=f"manually added {company.name}",
                detail="user-provided target",
                company_id=company.id,
            )
        )
        await db.commit()
        company_id = str(company.id)

    asyncio.create_task(run_pipeline(company_id))
    return {"status": "added", "company_id": company_id}


@router.post("/companies/{company_id}/research")
async def rerun_research(company_id: str):
    """
    Re-run the pipeline for one company. Clears any previous research so the
    research agent re-enriches it, then resets status to 'discovered' so the
    orchestrator drives it forward again (research -> draft -> approval).
    """
    async with AsyncSessionLocal() as db:
        company = await db.get(Company, company_id)
        if not company:
            return {"status": "not_found"}

        # Remove stale research so it gets fully re-done.
        existing = await db.execute(
            select(Research).where(Research.company_id == company.id)
        )
        for r in existing.scalars().all():
            await db.delete(r)

        company.status = "discovered"
        company.fit_score = None
        await db.commit()

    asyncio.create_task(run_pipeline(company_id))
    return {"status": "re-running", "company_id": company_id}
