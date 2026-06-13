import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import init_db
from api import companies, profile, run, log
from tg.bot import start_bot
from agents.followup import schedule_followup_checks

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("huntagent")


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()

    # Start the Telegram bot, but never let a bad/missing token kill the API.
    try:
        asyncio.create_task(start_bot())
    except Exception as e:  # pragma: no cover
        logger.warning(f"Telegram bot failed to start: {e}")

    asyncio.create_task(schedule_followup_checks())
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
