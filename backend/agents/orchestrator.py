"""
The core agent loop. Implements ReAct: Think -> Act -> Observe -> repeat.
Agents do not call each other directly.
They read and write shared state in Postgres.
The orchestrator decides what happens next based on company status.
"""
import asyncio
import logging

from sqlalchemy.ext.asyncio import AsyncSession

from models import Company, AgentLog
from agents import discovery, research, outreach, delivery
from tools.telegram_client import send_approval_request
from database import AsyncSessionLocal

log = logging.getLogger(__name__)

STATUS_TRANSITIONS = {
    "discovered": "researched",
    "researched": "draft_ready",
    "draft_ready": "pending_approval",  # human gate — loop pauses here
    "approved": "sent",
    "sent": "replied",  # or followup_due
}


async def log_action(
    db: AsyncSession, agent: str, action: str, detail: str = None, company_id=None
):
    entry = AgentLog(agent=agent, action=action, detail=detail, company_id=company_id)
    db.add(entry)
    await db.commit()


async def run_pipeline(company_id: str):
    """
    Entry point for a single company.
    Runs the full ReAct loop until it hits a human gate or terminal state.
    """
    async with AsyncSessionLocal() as db:
        company = await db.get(Company, company_id)
        if not company:
            return

        while True:
            status = company.status
            await log_action(
                db, "orchestrator", f"evaluating status: {status}", company_id=company.id
            )

            try:
                # THINK + ACT + OBSERVE

                if status == "discovered":
                    result = await research.run(company, db)
                    if result.fit_score < 7.0:
                        company.status = "skipped_low_fit"
                        await db.commit()
                        await log_action(
                            db,
                            "orchestrator",
                            f"skipped — fit score {result.fit_score}",
                            company_id=company.id,
                        )
                        break
                    company.status = "researched"
                    company.fit_score = result.fit_score
                    await db.commit()

                elif status == "researched":
                    draft = await outreach.draft(company, db)
                    company.status = "draft_ready"
                    await db.commit()
                    await log_action(
                        db,
                        "orchestrator",
                        "draft ready, sending to Telegram",
                        company_id=company.id,
                    )
                    await send_approval_request(company, draft)
                    break  # pause — resume via Telegram callback

                elif status == "approved":
                    result = await delivery.send(company, db)
                    company.status = "sent"
                    await db.commit()
                    await log_action(
                        db,
                        "orchestrator",
                        f"sent via {result.channel}",
                        company_id=company.id,
                    )
                    break

                else:
                    break

            except Exception as e:
                log.error(f"Pipeline error for company {company_id} at '{status}': {e}")
                await db.rollback()
                await log_action(
                    db,
                    "orchestrator",
                    f"error at {status}",
                    detail=str(e)[:500],
                    company_id=company.id,
                )
                break


async def run_discovery():
    """
    Triggered by POST /api/run.
    Discovery agent finds companies, then spawns a pipeline task per company.
    """
    async with AsyncSessionLocal() as db:
        companies = await discovery.run(db)

    # Spawn pipelines outside the discovery session so each runs independently.
    for company in companies:
        asyncio.create_task(run_pipeline(str(company.id)))
