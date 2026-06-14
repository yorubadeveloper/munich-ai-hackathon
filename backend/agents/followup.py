"""
Follow-up Agent.
Think: has it been 5 days since we sent? Did they reply?
Act: check Unipile for LinkedIn replies, check IMAP for email replies.
Observe: if reply — notify. If silence — draft follow-up, send to Telegram gate.
Runs as a background task every hour.
"""
import asyncio
import logging
from datetime import datetime

from sqlalchemy import select

from database import AsyncSessionLocal
from models import AgentLog, Company, Message
from tools.gemini_client import draft_followup_message
from tools.telegram_client import notify_reply, send_followup_approval
from tools.unipile_client import check_linkedin_replies

log = logging.getLogger(__name__)


async def check_and_followup():
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Message).where(Message.status == "sent"))
        sent_messages = result.scalars().all()

        for message in sent_messages:
            company = await db.get(Company, message.company_id)
            if not company:
                continue

            # Check for replies.
            if message.conversation_id and message.channel == "linkedin":
                replies = await check_linkedin_replies(message.conversation_id)
                if replies:
                    message.status = "replied"
                    message.replied_at = datetime.utcnow()
                    company.status = "replied"
                    db.add(
                        AgentLog(
                            agent="followup_agent",
                            action=f"reply detected from {company.name}",
                            company_id=company.id,
                        )
                    )
                    await db.commit()
                    await notify_reply(company, replies[0])
                    continue

            # Check if follow-up is due.
            if not message.sent_at:
                continue
            days_since = (datetime.utcnow() - message.sent_at).days
            if days_since >= 5 and message.followup_status == "pending":
                followup_body = await draft_followup_message(company, message)
                message.followup_draft = followup_body
                message.followup_status = "awaiting_approval"
                db.add(
                    AgentLog(
                        agent="followup_agent",
                        action=f"follow-up drafted for {company.name}",
                        detail=f"{days_since} days since last contact",
                        company_id=company.id,
                    )
                )
                await db.commit()
                await send_followup_approval(company, followup_body)


async def schedule_followup_checks():
    while True:
        try:
            await check_and_followup()
        except Exception as e:
            log.error(f"Followup check error: {e}")
        await asyncio.sleep(3600)  # every hour
