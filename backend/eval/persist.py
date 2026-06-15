import logging

from sqlalchemy import select

from database import AsyncSessionLocal
from eval.evaluator import EvalResult
from models import Company, EvidenceEvent

log = logging.getLogger(__name__)

async def save_evaluation_to_db(eval_result: EvalResult):
    try:
        async with AsyncSessionLocal() as db:
            # Find or create a dummy company for evaluation
            res = await db.execute(select(Company).where(Company.name == "System: Pioneer Evaluation"))
            company = res.scalar_one_or_none()
            if not company:
                company = Company(name="System: Pioneer Evaluation", status="approved")
                db.add(company)
                await db.commit()
                await db.refresh(company)

            # Persist eval result as evidence event
            event = EvidenceEvent(
                company_id=company.id,
                resource_name="Pioneer",
                artifact_type="pioneer_eval",
                payload=eval_result.model_dump(),
                status="success"
            )
            db.add(event)
            await db.commit()
            log.info(f"Successfully saved evaluation result to database for company {company.id}")
    except Exception as e:
        log.error(f"Failed to save evaluation to database: {e}")
