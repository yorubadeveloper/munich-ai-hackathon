"""
Outreach Agent.
Think: what channel, what tone, what specific hook makes this message not get ignored?
Act: Gemini drafts a message using company research + user bio.
Observe: save draft, hand off to Telegram gate.
"""
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from models import Company, Research, Message, UserProfile, AgentLog
from tools.gemini_client import draft_outreach_message


@dataclass
class OutreachDraft:
    id: str
    channel: str
    subject: str
    body: str


OUTREACH_PROMPT = """
Write a cold outreach message from {user_name} to a person at a company they want
to work with. The goal is a reply, not a resume dump.

WHO {user_name} IS:
{bio}

WHAT {user_name} HAS BUILT (use the ONE most relevant to THIS company; if none fit,
do not force it):
{projects}

Optional links (include AT MOST ONE, only if it genuinely strengthens the message):
{links}

THE COMPANY:
- Name: {company_name}
- What they do: {company_summary}
- Funding stage: {funding_stage}
- Recent news / signal: {recent_news}
- Role they are hiring: {job_title}
- Person you are writing to: {hiring_manager}{hiring_manager_role}
- Their tech stack: {tech_stack}

CHANNEL: {channel}
- linkedin: 1 to 3 short sentences, under 280 characters total, no greeting fluff,
  no signature, no links unless essential. Sound like a DM, not a cover letter.
- email: under 110 words, with a specific subject line. One short paragraph.

VOICE AND CONTENT RULES:
- Sound like a real engineer who did 5 minutes of homework, not a recruiter.
- Open with a concrete, specific hook about THEM (a product detail, the recent
  signal, something technical) - not "I came across your company".
- Then one line on what {user_name} actually builds that is relevant. Be concrete.
- Make the relevance obvious without saying "my experience aligns with your focus".
- One clear ask: a short call. Keep it low-pressure ("worth a quick chat?").
- Plain, direct language. Contractions are good.

BANNED (do not write any of these or anything like them):
- "I hope this message finds you well"
- "I am very passionate about" / "deeply passionate"
- "my experience in X aligns with Y" / "aligns with your focus/mission"
- "I'd love to" used more than once
- "caught my eye" / "reached out"
- em dashes, bullet points, hashtags, emojis
- generic praise with no specific detail

Return valid JSON only, no markdown, no extra text:
{{
  "subject": "specific subject line (email only, else empty string)",
  "body": "the message",
  "channel": "linkedin" | "email",
  "hook_used": "the one specific company detail you referenced"
}}
"""


async def draft(company: Company, db: AsyncSession) -> OutreachDraft:
    profile_result = await db.execute(select(UserProfile).limit(1))
    profile = profile_result.scalar_one_or_none()

    research_result = await db.execute(
        select(Research).where(Research.company_id == company.id)
    )
    research = research_result.scalar_one_or_none()

    # Choose channel:
    #  - LinkedIn if we can actually DM them (provider id or profile URL)
    #  - else email if we have a real address for the person
    #  - else fall back to LinkedIn URL if any, otherwise email (jobs@ fallback)
    has_linkedin = bool(
        research and (research.hiring_manager_provider_id or research.hiring_manager_linkedin)
    )
    has_email = bool(research and research.hiring_manager_email)
    if has_linkedin:
        channel = "linkedin"
    elif has_email:
        channel = "email"
    else:
        channel = "email"

    # Safe fallbacks so a thin/empty research row never crashes the draft.
    raw_text = company.raw_job_text or ""
    company_summary = (
        (research.recent_news if research and research.recent_news else None)
        or raw_text[:300]
        or company.name
    )

    # Compose the candidate's projects + links for the prompt.
    projects_text = (profile.projects if profile and profile.projects else "") or (
        "No specific projects provided; lean on the bio."
    )
    link_parts = []
    if profile and profile.github_url:
        link_parts.append(f"GitHub: {profile.github_url}")
    if profile and profile.portfolio_url:
        link_parts.append(f"Portfolio: {profile.portfolio_url}")
    if profile and profile.linkedin_url:
        link_parts.append(f"LinkedIn: {profile.linkedin_url}")
    links_text = " | ".join(link_parts) if link_parts else "none"

    hm_role = research.hiring_manager_role if research else None
    prompt = OUTREACH_PROMPT.format(
        user_name=profile.name,
        bio=profile.bio or "",
        projects=projects_text,
        links=links_text,
        company_name=company.name,
        company_summary=company_summary,
        funding_stage=(research.funding_stage if research else None) or "unknown",
        recent_news=(research.recent_news if research else None) or "",
        job_title=profile.role,
        hiring_manager=(research.hiring_manager_name if research else None) or "the team",
        hiring_manager_role=f" ({hm_role})" if hm_role else "",
        tech_stack=", ".join((research.tech_stack if research else None) or []),
        channel=channel,
    )

    result = await draft_outreach_message(prompt)

    # The channel is decided by us (based on which contact we actually have),
    # not the LLM — it sometimes flips it. Enforce ours.
    body = result.get("body") or "(draft generation failed — please retry)"
    if channel == "linkedin" and len(body) > 300:
        # Keep LinkedIn DMs short; trim at a sentence boundary if possible.
        trimmed = body[:300]
        last_dot = trimmed.rfind(".")
        body = (trimmed[: last_dot + 1] if last_dot > 150 else trimmed).strip()

    message = Message(
        company_id=company.id,
        channel=channel,
        subject=result.get("subject") if channel == "email" else None,
        draft_body=body,
        status="pending",
    )
    db.add(message)

    entry = AgentLog(
        agent="outreach_agent",
        action=f"drafted {channel} message for {company.name}",
        detail=result.get("hook_used"),
        company_id=company.id,
    )
    db.add(entry)
    await db.commit()
    await db.refresh(message)

    return OutreachDraft(
        id=str(message.id),
        channel=message.channel,
        subject=message.subject or "",
        body=message.draft_body,
    )
