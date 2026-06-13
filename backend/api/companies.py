from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from models import Company, Research
from database import get_db

router = APIRouter()


@router.get("/companies")
async def get_companies(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Company).order_by(Company.discovered_at.desc())
    )
    companies = result.scalars().all()
    out = []
    for c in companies:
        research_result = await db.execute(
            select(Research).where(Research.company_id == c.id)
        )
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
            }
        )
    return out
