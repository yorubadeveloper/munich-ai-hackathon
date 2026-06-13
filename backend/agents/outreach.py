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
You are writing a cold outreach message for {user_name}.

About {user_name}:
{bio}

What {user_name} has built (pick the ONE most relevant to this company and reference it concretely):
{projects}

Links you may weave in naturally if relevant: {links}

About the company:
- Name: {company_name}
- What they do: {company_summary}
- Funding stage: {funding_stage}
- Recent news: {recent_news}
- Hiring for: {job_title}
- Hiring manager: {hiring_manager} (use if known, otherwise address generally)
- Tech stack: {tech_stack}

Channel: {channel}
- If linkedin: max 300 characters, punchy, no fluff
- If email: max 150 words, include a subject line

Hard rules — do not break any of these:
1. Write like a human engineer talking to another engineer
2. Lead with who {user_name} is and what they build — NOT what they want
3. Reference exactly ONE specific thing about the company
4. Reference exactly ONE specific project {user_name} built that is relevant to them
5. ONE ask only: a 20-minute call
6. No "I hope this message finds you well"
7. No "I am very passionate about"
8. No em dashes
9. No bullet points in the message body
10. If a portfolio or GitHub link is genuinely relevant, you may include ONE link

Return valid JSON only, no markdown, no extra text:
{{
  "subject": "...",
  "body": "...",
  "channel": "linkedin" | "email",
  "hook_used": "one sentence explaining what specific detail you referenced"
}}
"""


async def draft(company: Company, db: AsyncSession) -> OutreachDraft:
    profile_result = await db.execute(select(UserProfile).limit(1))
    profile = profile_result.scalar_one_or_none()

    research_result = await db.execute(
        select(Research).where(Research.company_id == company.id)
    )
    research = research_result.scalar_one_or_none()

    # Choose channel: prefer LinkedIn if hiring manager URL exists.
    channel = "linkedin" if research and research.hiring_manager_linkedin else "email"

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
        tech_stack=", ".join((research.tech_stack if research else None) or []),
        channel=channel,
    )

    result = await draft_outreach_message(prompt)

    message = Message(
        company_id=company.id,
        channel=result.get("channel", channel),
        subject=result.get("subject"),
        draft_body=result.get("body") or "(draft generation failed — please retry)",
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
