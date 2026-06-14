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


LINKEDIN_PROMPT = """
Write a substantial, high-impact LinkedIn direct message from {user_name} to {hiring_manager}{hiring_manager_role} at {company_name}.
This is a real DM (not a tiny note), so make it detailed and compelling.

WHO {user_name} IS:
{bio}

WHAT {user_name} HAS BUILT:
{projects}

THE COMPANY:
- Name: {company_name}
- What they do: {company_summary}
- Hiring for: {job_title}
- Tech stack: {tech_stack}

STRICT BLUEPRINT (90-130 WORDS, 3 SHORT PARAGRAPHS):
- Hi {hiring_manager},
- Paragraph 1 (The Hook): A specific, technical comment about what {company_name} is building and the hard engineering it implies (cite their actual product niche and scale, e.g. AI agents for CPQ sales in machinery, high-throughput LLM pipelines, SAP/Salesforce integrations).
- Paragraph 2 (Your Pitch + Project): State you are a {job_title} and pitch your hands-on engineering with a specific relevant project from your list (e.g. SyncStudy supporting 1k users on OpenAI/AWS, or HTML4PDF scaling on AWS) and why it maps to their stack.
- Paragraph 3 (The Ask): Connect your strengths to their challenges and ask if they're open to a brief 15-minute call.

HARD RULES:
- Sound like a real, sharp engineer writing to a peer. No corporate fluff.
- Absolutely NO generic praise like "your focus is truly compelling" or "your work is deeply interesting".
- Lead with what you BUILD, not what you want.
- No emojis, no hashtags, no bullet points, no em dashes, no links.

Return valid JSON only, no markdown, no extra text:
{{
  "subject": "",
  "body": "the full multi-paragraph DM body",
  "channel": "linkedin",
  "hook_used": "one sentence explaining the hook you used"
}}
"""


# Separate SHORT note used ONLY when falling back to a connection invite
# (LinkedIn caps invite notes at 300 characters).
LINKEDIN_NOTE_PROMPT = """
Write a LinkedIn CONNECTION-REQUEST note from {user_name} to {hiring_manager} at {company_name}.
LinkedIn caps this at 300 characters, so it MUST be short and tight.

About {user_name}: {bio}
What {user_name} built: {projects}
Company: {company_name} — {company_summary}
Role: {job_title}

STRICT 3-SENTENCE BLUEPRINT (UNDER 290 CHARACTERS TOTAL):
- Sentence 1 (Hook): "Hi {hiring_manager}, saw {company_name} is building [their specific niche]."
- Sentence 2 (Pitch): "I'm a {job_title} and recently built [ONE specific project, short]."
- Sentence 3 (Ask): "Worth a short chat about the role?"

HARD RULES:
- Under 290 characters total. Count carefully. Be ruthless.
- Exactly 3 sentences. No links, no emojis, no hashtags, no em dashes, no signature.

Return valid JSON only:
{{
  "subject": "",
  "body": "the 3-sentence note under 290 characters",
  "channel": "linkedin",
  "hook_used": "the hook"
}}
"""


EMAIL_PROMPT = """
Write a professional, multi-paragraph cold email pitch from {user_name} to {hiring_manager}{hiring_manager_role} at {company_name}.

WHO {user_name} IS:
{bio}

WHAT {user_name} HAS BUILT:
{projects}

Links you may weave in naturally at the bottom: {links}

THE COMPANY:
- Name: {company_name}
- What they do: {company_summary}
- Funding stage: {funding_stage}
- Recent news / signal: {recent_news}
- Hiring for: {job_title}
- Tech stack: {tech_stack}

STRICT MULTI-PARAGRAPH EMAIL BLUEPRINT (220-300 WORDS, SUBSTANTIAL AND DETAILED):
- Subject: A highly specific, non-spammy subject line referencing engineering scale and your name/role.
- Hi {hiring_manager},
- Paragraph 1 (The Hook - 2-3 sentences): Open with a specific, technical observation about what {company_name} is building and the hard engineering problems it implies (e.g. automating multi-modal mechanical sales CPQ, scaling high-throughput agent platforms to millions of LLM calls, enterprise SAP/Salesforce/PLM write-backs, tenant isolation). Show you actually understand their domain.
- Paragraph 2 (Your Project Pitch - 3-4 sentences): Introduce {user_name} as a {job_title} and pitch your hands-on engineering in depth. Walk through 1-2 specific projects from your list with concrete detail: what you built, the stack used, the scale/metrics achieved, and what was hard about it (e.g. SyncStudy supporting 1k users on OpenAI/AWS, HTML4PDF API engineered for reliable scaling on AWS). Be concrete and technical.
- Paragraph 3 (Value & Challenges - 2-3 sentences): Connect your specific technical strengths directly to the problems {company_name} is scaling — robust backend services, high-throughput ETL/LLM pipelines, multi-tenant security, complex enterprise integrations, cost/latency optimization. Make it obvious why you'd contribute fast.
- Paragraph 4 (The Ask - 1-2 sentences): A confident but low-pressure call to action asking if they would be open to a short 15-20 minute call to discuss how your backend/cloud engineering could help {company_name}'s scale challenges.
- Thanks,
  {user_name}
  {links}

HARD RULES:
- Write a full, substantial email. Do NOT be terse. Aim for 220-300 words of genuinely useful content.
- Sound like a real, sharp engineer writing to a peer, not a recruiter or an AI.
- Absolutely NO generic praise fluff like "I find your focus truly compelling" or "your work is deeply interesting".
- Lead with what you BUILD and the hard problems you've solved, not what you want.
- No emojis, no hashtags, no bullet points, no em dashes.

Return valid JSON only, no markdown, no extra text:
{{
  "subject": "your subject line",
  "body": "the full multi-paragraph email body",
  "channel": "email",
  "hook_used": "one sentence explaining the hook you used"
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
    template = LINKEDIN_PROMPT if channel == "linkedin" else EMAIL_PROMPT

    prompt = template.format(
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


async def draft_linkedin_note(company: Company, db: AsyncSession) -> str:
    """
    Generate a SHORT (<=300 char) LinkedIn connection-request note on demand.
    Used by the delivery agent when a DM falls back to a connection invite.
    """
    profile_result = await db.execute(select(UserProfile).limit(1))
    profile = profile_result.scalar_one_or_none()

    research_result = await db.execute(
        select(Research).where(Research.company_id == company.id)
    )
    research = research_result.scalar_one_or_none()

    projects_text = (profile.projects if profile and profile.projects else "") or (
        "various backend and AI projects"
    )
    company_summary = (
        (research.recent_news if research and research.recent_news else None)
        or (company.raw_job_text or "")[:200]
        or company.name
    )

    prompt = LINKEDIN_NOTE_PROMPT.format(
        user_name=profile.name if profile else "",
        bio=(profile.bio if profile else "") or "",
        projects=projects_text,
        company_name=company.name,
        company_summary=company_summary,
        job_title=profile.role if profile else "Software Engineer",
        hiring_manager=(research.hiring_manager_name if research else None) or "there",
    )
    result = await draft_outreach_message(prompt)
    note = (result.get("body") or "").strip()
    return note[:300]

