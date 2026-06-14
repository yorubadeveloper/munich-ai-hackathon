from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models import Company, Research

router = APIRouter()


@router.get("/companies")
async def get_companies(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Company).order_by(Company.discovered_at.desc()))
    companies = result.scalars().all()
    out = []
    for c in companies:
        research_result = await db.execute(select(Research).where(Research.company_id == c.id))
        research = research_result.scalar_one_or_none()
        out.append(
            {
                "id": str(c.id),
                "name": c.name,
                "status": c.status,
                "fit_score": c.fit_score,
                "source": c.source,
                "discovered_at": c.discovered_at.isoformat(),
                "funding_stage": research.funding_stage if research else None,
                "tech_stack": research.tech_stack if research else [],
                "hiring_manager": research.hiring_manager_name if research else None,
                "hiring_manager_role": research.hiring_manager_role if research else None,
                "hiring_manager_linkedin": research.hiring_manager_linkedin if research else None,
                "recent_news": research.recent_news if research else None,
                "fit_reasoning": research.fit_reasoning if research else None,
            }
        )
    return out


@router.delete("/companies/{company_id}")
async def delete_company(company_id: str, db: AsyncSession = Depends(get_db)):
    """
    Delete a company and all of its associated records (research, messages, logs)
    to keep foreign key references clean.
    """
    from sqlalchemy import delete

    from models import AgentLog, Message, Research

    # Delete linked child rows first.
    await db.execute(delete(Research).where(Research.company_id == company_id))
    await db.execute(delete(Message).where(Message.company_id == company_id))
    await db.execute(delete(AgentLog).where(AgentLog.company_id == company_id))

    # Nuke the parent company.
    company = await db.get(Company, company_id)
    if company:
        await db.delete(company)
        await db.commit()
        return {"status": "deleted", "company_id": company_id}
    return {"status": "not_found"}
