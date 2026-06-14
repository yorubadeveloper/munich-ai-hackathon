from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models import AgentLog

router = APIRouter()


@router.get("/log")
async def get_log(limit: int = 50, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(AgentLog).order_by(AgentLog.created_at.desc()).limit(limit))
    logs = result.scalars().all()
    return [
        {
            "id": str(log_entry.id),
            "agent": log_entry.agent,
            "action": log_entry.action,
            "detail": log_entry.detail,
            "company_id": str(log_entry.company_id) if log_entry.company_id else None,
            "created_at": log_entry.created_at.isoformat(),
        }
        for log_entry in logs
    ]
