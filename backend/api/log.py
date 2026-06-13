from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from models import AgentLog
from database import get_db

router = APIRouter()


@router.get("/log")
async def get_log(limit: int = 50, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(AgentLog).order_by(AgentLog.created_at.desc()).limit(limit)
    )
    logs = result.scalars().all()
    return [
        {
            "id": str(l.id),
            "agent": l.agent,
            "action": l.action,
            "detail": l.detail,
            "company_id": str(l.company_id) if l.company_id else None,
            "created_at": l.created_at.isoformat(),
        }
        for l in logs
    ]
