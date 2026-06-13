"""
Research Agent.
Think: what do I need to know about this company to score fit and draft outreach?
Act: Tavily searches for funding, hiring manager, tech signals, recent news.
Observe: Gemini synthesises into structured profile + fit score.
"""
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from models import Company, Research, UserProfile, AgentLog
from tools.tavily_client import search
from tools.gemini_client import synthesise_research, score_fit


@dataclass
class ResearchResult:
    fit_score: float
    funding_stage: str
    hiring_manager_name: str
    hiring_manager_linkedin: str
    tech_stack: list[str]
    recent_news: str
    fit_reasoning: str


async def run(company: Company, db: AsyncSession) -> ResearchResult:
    profile_result = await db.execute(select(UserProfile).limit(1))
    profile = profile_result.scalar_one_or_none()

    queries = [
        f"{company.name} funding round 2024 2025",
        f"{company.name} CTO engineering hiring manager LinkedIn",
        f"{company.name} tech stack backend engineering",
        f"{company.name} news product launch 2025",
    ]

    raw_results = []
    for q in queries:
        results = await search(q, max_results=3)
        raw_results.extend(results)

    # OBSERVE: synthesise with Gemini.
    enriched = await synthesise_research(company.name, raw_results)
    fit = await score_fit(enriched, profile)

    research = Research(
        company_id=company.id,
        funding_stage=enriched.get("funding_stage"),
        headcount_estimate=enriched.get("headcount"),
        tech_stack=enriched.get("tech_stack", []),
        hiring_manager_name=enriched.get("hiring_manager_name"),
        hiring_manager_linkedin=enriched.get("hiring_manager_linkedin"),
        hiring_manager_email=enriched.get("hiring_manager_email"),
        recent_news=enriched.get("recent_news"),
        fit_reasoning=fit.get("reasoning"),
    )
    db.add(research)

    entry = AgentLog(
        agent="research_agent",
        action=f"enriched {company.name}",
        detail=f"fit score: {fit.get('score')} · {enriched.get('funding_stage')}",
        company_id=company.id,
    )
    db.add(entry)
    await db.commit()

    return ResearchResult(
        fit_score=float(fit.get("score", 0) or 0),
        funding_stage=enriched.get("funding_stage", "") or "",
        hiring_manager_name=enriched.get("hiring_manager_name", "") or "",
        hiring_manager_linkedin=enriched.get("hiring_manager_linkedin", "") or "",
        tech_stack=enriched.get("tech_stack", []) or [],
        recent_news=enriched.get("recent_news", "") or "",
        fit_reasoning=fit.get("reasoning", "") or "",
    )
