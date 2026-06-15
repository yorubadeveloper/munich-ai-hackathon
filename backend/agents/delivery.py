"""
Delivery Agent.
Think: message is approved — what channel, what recipient, send it.
Act: Unipile for LinkedIn DM, Resend for email.
Observe: store conversation ID for reply tracking.
"""

import logging
from dataclasses import dataclass
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import AgentLog, Company, Message, Research
from tools.unipile_client import send_email, send_linkedin_message, send_linkedin_invite

log = logging.getLogger(__name__)


@dataclass
class DeliveryResult:
    channel: str
    conversation_id: str
    fallback_to_email: bool = False


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

    # ── LinkedIn cascade: DM -> Invite+Note -> Email fallback ──
    if (
        message.channel == "linkedin"
        and research
        and research.hiring_manager_provider_id
    ):
        provider_id = research.hiring_manager_provider_id
        body = message.final_body or message.draft_body

        # Tier 1: try a direct DM (works if already connected; free).
        log.info(f"Attempting LinkedIn DM to {provider_id}...")
        result = await send_linkedin_message(provider_id, body)
        conversation_id = result.get("chat_id")

        # Tier 2: DM failed (likely not connected) -> connection invite + SHORT note.
        if not conversation_id:
            log.info("DM failed — falling back to a connection invite with a short note...")
            # Generate a fresh SHORT (<=300 char) note for the invite — the long
            # DM body won't fit LinkedIn's invite-note limit.
            from agents.outreach import draft_linkedin_note
            note = await draft_linkedin_note(company, db)
            if not note:
                note = body[:300]
            db.add(
                AgentLog(
                    agent="delivery_agent",
                    action=f"DM to {company.name} failed — sending connection invite with note",
                    detail=(result.get("error") or "")[:200],
                    company_id=company.id,
                )
            )
            await db.commit()
            invite_result = await send_linkedin_invite(provider_id, note)
            conversation_id = invite_result.get("chat_id")

        # Tier 3: invite also failed -> reset to draft an EMAIL for re-approval.
        if not conversation_id:
            log.warning("LinkedIn invite failed too. Resetting to draft an email for approval...")
            # Clear LinkedIn contact so the next draft uses email.
            research.hiring_manager_provider_id = None
            research.hiring_manager_linkedin = None
            company.status = "researched"
            await db.delete(message)
            db.add(
                AgentLog(
                    agent="delivery_agent",
                    action=f"LinkedIn fully failed for {company.name} — drafting email for your approval",
                    company_id=company.id,
                )
            )
            await db.commit()
            # Signal the orchestrator to re-draft as email + re-approve.
            return DeliveryResult(channel="email", conversation_id="", fallback_to_email=True)

    # ── Email delivery ──
    if message.channel == "email":
        recipient_email = research.hiring_manager_email if research else None
        if not recipient_email:
            recipient_email = _fallback_email(company)

        log.info(f"Delivering email to {recipient_email} via Resend...")
        subject = message.subject or f"Quick intro — {company.name}"
        body = message.final_body or message.draft_body

        await send_email(
            to=recipient_email,
            subject=subject,
            body=body,
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
