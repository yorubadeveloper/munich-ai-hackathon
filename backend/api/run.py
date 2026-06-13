from fastapi import APIRouter
from agents.orchestrator import run_discovery
import asyncio

router = APIRouter()


@router.post("/run")
async def trigger_run():
    asyncio.create_task(run_discovery())
    return {"status": "started"}
