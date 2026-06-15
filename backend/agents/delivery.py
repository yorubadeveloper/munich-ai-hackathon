"""
Delivery Agent.
Think: message is approved — what channel, what recipient, send it.
Act: Unipile for LinkedIn DM, Resend for email.
Observe: store conversation ID for reply tracking.
"""

from dataclasses import dataclass
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import AgentLog, Company, Message, Research
from tools.unipile_client import send_email, send_linkedin_dm


@dataclass
class DeliveryResult:
    channel: str
    conversation_id: str


def _fallback_email(company: Company) -> str:
    """Derive a best-effort jobs@ address from the company website."""
    website = company.website or ""
    domain = website.replace("https://", "").replace("http://", "").replace("www.", "").split("/")[0].strip()
    if not domain:
        domain = "example.com"
    return f"jobs@{domain}"


async def send(company: Company, db: AsyncSession) -> DeliveryResult:
    message_result = await db.execute(
        select(Message).where(Message.company_id == company.id, Message.status == "approved")
    )
    message = message_result.scalar_one_or_none()
    if not message:
        raise ValueError(f"No approved message found for company {company.id}")

    research_result = await db.execute(select(Research).where(Research.company_id == company.id))
    research = research_result.scalar_one_or_none()

    conversation_id = None

    if (
        message.channel == "linkedin"
        and research
        and (research.hiring_manager_provider_id or research.hiring_manager_linkedin)
    ):
        # Prefer Unipile's provider id (reliable for DMs); fall back to URL.
        recipient = research.hiring_manager_provider_id or research.hiring_manager_linkedin
        result = await send_linkedin_dm(
            recipient_linkedin_url=recipient,
            message=message.final_body or message.draft_body,
        )
        conversation_id = result.get("chat_id")
    else:
        recipient_email = research.hiring_manager_email if research else None
        if not recipient_email:
            recipient_email = _fallback_email(company)
        await send_email(
            to=recipient_email,
            subject=message.subject or f"Quick intro — {company.name}",
            body=message.final_body or message.draft_body,
        )
        conversation_id = f"email:{recipient_email}"

    message.status = "sent"
    message.sent_at = datetime.now(timezone.utc)
    message.conversation_id = conversation_id

    entry = AgentLog(
        agent="delivery_agent",
        action=f"sent via {message.channel} to {company.name}",
        detail=conversation_id,
        company_id=company.id,
    )
    db.add(entry)
    await db.commit()

    return DeliveryResult(channel=message.channel, conversation_id=conversation_id or "")
