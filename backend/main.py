import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from agents.followup import schedule_followup_checks
from api import companies, log, profile, run
from database import init_db
from tg.bot import start_bot

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("huntagent")


async def resume_stuck_pipelines():
    """
    On server boot, check for any companies stuck in active transient states
    (e.g., killed mid-execution by a server reload) and reset/re-spawn them.
    """
    from sqlalchemy import select

    from agents.orchestrator import run_pipeline
    from database import AsyncSessionLocal
    from models import Company

    await asyncio.sleep(2)  # wait for DB init and bot polling to start
    logger.info("Checking for orphaned/stuck pipelines on startup...")

    async with AsyncSessionLocal() as db:
        res = await db.execute(
            select(Company).where(
                Company.status.in_(["researching", "drafting", "delivering"])
            )
        )
        stuck_companies = res.scalars().all()
        if not stuck_companies:
            logger.info("No stuck pipelines found. All clean.")
            return

        logger.info(f"Found {len(stuck_companies)} stuck pipelines. Healing...")
        for c in stuck_companies:
            old_status = c.status
            if c.status == "researching":
                c.status = "discovered"
            elif c.status == "drafting":
                c.status = "researched"
            elif c.status == "delivering":
                c.status = "approved"
            
            logger.info(f"Resetting '{c.name}': {old_status} -> {c.status}")
            await db.commit()
            asyncio.create_task(run_pipeline(str(c.id)))


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()

    # Start the Telegram bot, but never let a bad/missing token kill the API.
    try:
        asyncio.create_task(start_bot())
    except Exception as e:  # pragma: no cover
        logger.warning(f"Telegram bot failed to start: {e}")

    asyncio.create_task(schedule_followup_checks())
    asyncio.create_task(resume_stuck_pipelines())
    yield


app = FastAPI(title="HuntAgent", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(companies.router, prefix="/api")
app.include_router(profile.router, prefix="/api")
app.include_router(run.router, prefix="/api")
app.include_router(log.router, prefix="/api")


@app.get("/")
async def root():
    return {"service": "HuntAgent", "status": "ok"}


@app.get("/health")
async def health():
    return {"status": "healthy"}
