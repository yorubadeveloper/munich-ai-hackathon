"""
Research Agent.
Think: who is the right person to reach out to at this company, and what do I
       need to know to write a credible intro?
Act: 1) Find the decision-maker via LinkedIn people-search (Unipile) on behalf of
        the user's connected account — CTO / VP Eng / Head of Eng / founder.
     2) Tavily searches for funding, tech signals, recent news.
Observe: Gemini synthesises company facts; the resolved person (name, role,
         LinkedIn URL, and Unipile provider id for DMs) is stored on Research.
"""

import logging
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import AgentLog, Company, Research, UserProfile
from tools.gemini_client import pick_best_contact, score_fit, synthesise_research
from tools.tavily_client import search
from tools.unipile_client import search_linkedin_people

log = logging.getLogger(__name__)


# Decision-maker titles we want to reach, most senior / most relevant first.
TARGET_TITLES = [
    "CTO",
    "VP Engineering",
    "Head of Engineering",
    "Founder",
    "Co-Founder",
    "Engineering Manager",
    "Head of Talent",
    "Technical Recruiter",
]


@dataclass
class ResearchResult:
    fit_score: float
    funding_stage: str
    hiring_manager_name: str
    hiring_manager_linkedin: str
    tech_stack: list[str]
    recent_news: str
    fit_reasoning: str


async def _find_decision_maker(company: Company, profile: UserProfile) -> dict:
    """
    Use Unipile LinkedIn people-search to find the best person to contact at the
    company. Returns the chosen contact dict (or {} if none found).
    """
    # One focused query: senior eng/leadership titles at this company.
    role_keywords = "CTO OR VP Engineering OR Head of Engineering OR Founder"
    raw_candidates = await search_linkedin_people(
        keywords=role_keywords,
        company_keyword=company.name,
        limit=8,
    )
    if not raw_candidates:
        return {}

    # Strict Company Verification: Only keep candidates who actually work there.
    # We check if the company name appears in their parsed company, headline, or role.
    candidates = []
    co_name_lower = company.name.lower().strip()
    for c in raw_candidates:
        cand_co = (c.get("company") or "").lower().strip()
        cand_hl = (c.get("headline") or "").lower().strip()
        cand_role = (c.get("role") or "").lower().strip()

        # Match if the target company name appears as a word/substring in their current
        # company, headline, or role (e.g. "Atira" in "Atira GmbH" or "Head of Engineering at Atira").
        if (
            co_name_lower in cand_co
            or co_name_lower in cand_hl
            or f"at {co_name_lower}" in cand_hl
            or f"at {co_name_lower}" in cand_role
        ):
            candidates.append(c)
        else:
            log.info(
                f"Filtered out candidate: {c.get('name')} works at '{c.get('company') or 'unknown'}' "
                f"(mismatch for target company '{company.name}')"
            )

    if not candidates:
        log.warning(f"No verified decision-maker found at '{company.name}' on LinkedIn.")
        return {}

    # Let Gemini pick the single best person from the VERIFIED list.
    best = await pick_best_contact(company.name, profile.role, candidates)
    if best:
        return best

    # Fallback: first verified candidate whose role looks senior, else the first.
    for c in candidates:
        role = (c.get("role") or "").lower()
        if any(t.lower() in role for t in ["cto", "founder", "vp", "head"]):
            return c
    return candidates[0]


async def run(company: Company, db: AsyncSession) -> ResearchResult:
    profile_result = await db.execute(select(UserProfile).limit(1))
    profile = profile_result.scalar_one_or_none()

    # ── ACT 1: find the person (the whole point — warm/cold intro target) ──
    contact = await _find_decision_maker(company, profile)

    # ── ACT 2: company facts via web search ──
    # If the user provided a domain/website (e.g. atira.ai), scope searches to it.
    site_filter = f"site:{company.website.replace('https://','').replace('http://','').replace('www.','').split('/')[0]}" if company.website else ""

    queries = [
        f"{company.name} {site_filter} funding round" if site_filter else f"{company.name} funding round",
        f"{company.name} {site_filter} product about OR mission"
        if site_filter
        else f"{company.name} tech stack engineering blog",
        f"{company.name} product launch news",
    ]
    raw_results = []

    # If the user provided a specific Job Posting URL (e.g. Ashby/Greenhouse),
    # query Tavily specifically for it. Since Tavily uses headless browsers,
    # it easily bypasses SPA/JS-only blank screens and extracts the full JD!
    if company.job_url:
        log.info(f"Targeting specific job URL via Tavily: {company.job_url}")
        job_results = await search(company.job_url, max_results=1)
        if job_results:
            raw_results.extend(job_results)

    for q in queries:
        results = await search(q, max_results=3)
        raw_results.extend(results)

    # OBSERVE: synthesise company facts with Gemini.
    enriched = await synthesise_research(company.name, raw_results)

    # Critical: inject the raw job description text (if available) into the
    # enrichment data before scoring. This guarantees the fit evaluator sees the
    # exact tech requirements from the posting, even if generic web searches missed them!
    if company.raw_job_text:
        enriched["job_description_requirements"] = company.raw_job_text

    fit = await score_fit(enriched, profile)

    # Prefer the LinkedIn-verified contact; fall back to whatever Gemini guessed.
    hm_name = contact.get("name") or enriched.get("hiring_manager_name")
    hm_linkedin = contact.get("profile_url") or enriched.get("hiring_manager_linkedin")
    hm_role = contact.get("role")
    hm_provider = contact.get("provider_id")

    research = Research(
        company_id=company.id,
        funding_stage=enriched.get("funding_stage"),
        headcount_estimate=enriched.get("headcount"),
        tech_stack=enriched.get("tech_stack", []),
        hiring_manager_name=hm_name,
        hiring_manager_linkedin=hm_linkedin,
        hiring_manager_email=enriched.get("hiring_manager_email"),
        hiring_manager_role=hm_role,
        hiring_manager_provider_id=hm_provider,
        recent_news=enriched.get("recent_news"),
        fit_reasoning=fit.get("reasoning"),
    )
    db.add(research)

    person_note = f"{hm_name} ({hm_role})" if hm_name and hm_role else (hm_name or "no contact found")
    db.add(
        AgentLog(
            agent="research_agent",
            action=f"enriched {company.name}",
            detail=f"fit {fit.get('score')} · {enriched.get('funding_stage')} · contact: {person_note}",
            company_id=company.id,
        )
    )
    await db.commit()

    return ResearchResult(
        fit_score=float(fit.get("score", 0) or 0),
        funding_stage=enriched.get("funding_stage", "") or "",
        hiring_manager_name=hm_name or "",
        hiring_manager_linkedin=hm_linkedin or "",
        tech_stack=enriched.get("tech_stack", []) or [],
        recent_news=enriched.get("recent_news", "") or "",
        fit_reasoning=fit.get("reasoning", "") or "",
    )
