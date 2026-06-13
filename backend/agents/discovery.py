"""
Discovery Agent.
Think: given the candidate's niche, stage, size, and geography preferences,
       what precise searches surface REAL, on-target open roles?
Act: Tavily search across job boards and company pages using profile-driven queries.
Observe: run an LLM relevance gate to drop listicles/aggregators/off-target noise,
         clean up the company name, deduplicate, then write to DB.
"""
import logging
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from models import Company, UserProfile, AgentLog
from tools.tavily_client import search
from tools.gliner_client import extract_job_entities
from tools.gemini_client import check_relevance

log = logging.getLogger(__name__)

# Domains that are aggregators / listicles / directories — never a single
# hiring company, so we drop their URLs outright before spending an LLM call.
AGGREGATOR_DOMAINS = {
    "indeed.com",
    "glassdoor.com",
    "ziprecruiter.com",
    "monster.com",
    "simplyhired.com",
    "talent.com",
    "jooble.org",
    "neuvoo.com",
    "careerjet.com",
    "jobrapido.com",
    "medium.com",
    "wikipedia.org",
    "reddit.com",
    "quora.com",
    "youtube.com",
    "crunchbase.com",
    "builtin.com",
    "themuse.com",
}


def _registry_year() -> int:
    return datetime.utcnow().year


def _build_queries(profile: UserProfile) -> list[str]:
    """Profile-driven, current, precise queries. No hardcoded city/year."""
    role = profile.role
    seniority = (profile.seniority or "").strip()
    role_phrase = f"{seniority} {role}".strip()
    location = profile.location
    stack = ", ".join((profile.stack or [])[:3])
    industries = [i for i in (profile.target_industries or []) if i]
    stages = [s for s in (profile.target_funding_stages or []) if s]
    size = (profile.company_size or "").strip()
    year = _registry_year()

    industry_clause = f"({' OR '.join(industries)})" if industries else ""
    stage_clause = f"({' OR '.join(stages)})" if stages else ""

    queries: list[str] = []

    # 1. Wellfound (AngelList) — startup-focused, real roles.
    queries.append(
        f'"{role_phrase}" {industry_clause} "{location}" site:wellfound.com'.strip()
    )

    # 2. Greenhouse boards — company ATS pages = real openings.
    queries.append(
        f'"{role_phrase}" {industry_clause} {stack} "{location}" site:boards.greenhouse.io'.strip()
    )

    # 3. Lever boards — same idea, different ATS.
    queries.append(
        f'"{role_phrase}" {industry_clause} "{location}" site:jobs.lever.co'.strip()
    )

    # 4. "Who is hiring" style, scoped to industry + stage + now.
    queries.append(
        f"{industry_clause} {stage_clause} startup hiring {role_phrase} {location} {year}".strip()
    )

    # 5. Direct careers-page intent for the niche.
    queries.append(
        f'{industry_clause} {size} startup "{role_phrase}" careers "{location}" {year}'.strip()
    )

    # Collapse whitespace and drop empties.
    return [" ".join(q.split()) for q in queries if q.strip()]


def _domain(url: str) -> str:
    d = (
        (url or "")
        .replace("https://", "")
        .replace("http://", "")
        .replace("www.", "")
        .split("/")[0]
        .lower()
    )
    return d


def _is_aggregator(url: str) -> bool:
    d = _domain(url)
    return any(d == agg or d.endswith("." + agg) for agg in AGGREGATOR_DOMAINS)


async def run(db: AsyncSession) -> list[Company]:
    profile_result = await db.execute(select(UserProfile).limit(1))
    profile = profile_result.scalar_one_or_none()
    if not profile:
        log.warning("No user profile found. Seed one first.")
        return []

    queries = _build_queries(profile)
    discovered: list[Company] = []
    seen_urls: set[str] = set()
    kept = 0
    dropped = 0

    for query in queries:
        results = await search(query, max_results=6)

        for r in results:
            url = r.get("url")
            if not url or url in seen_urls:
                continue
            seen_urls.add(url)

            # Cheap pre-filter: drop known aggregator/listicle domains.
            if _is_aggregator(url):
                dropped += 1
                continue

            # Dealbreaker check (cheap, before any LLM call).
            raw_text = (r.get("content", "") + " " + r.get("title", "")).lower()
            if any(d.lower() in raw_text for d in (profile.dealbreakers or [])):
                dropped += 1
                continue

            # DB-level dedup.
            existing = await db.execute(
                select(Company).where(Company.job_url == url)
            )
            if existing.scalar_one_or_none():
                continue

            # LLM relevance gate — the main quality lever.
            verdict = await check_relevance(r, profile)
            if not verdict.get("relevant", False):
                dropped += 1
                continue

            # Clean company name: prefer the gate's name, then GLiNER, then a
            # cleaned title (strip trailing " | site" / " - site" noise).
            entities = await extract_job_entities(r.get("content", ""))
            title = (r.get("title", "") or "").split(" | ")[0].split(" - ")[0]
            name = (
                verdict.get("company_name")
                or entities.get("company_name")
                or title
                or "Unknown"
            )[:80].strip()

            company = Company(
                name=name,
                website=url,
                job_url=url,
                source=_domain(url),
                raw_job_text=(r.get("content", "") or "")[:4000],
                status="discovered",
            )
            db.add(company)
            await db.commit()
            await db.refresh(company)
            discovered.append(company)
            kept += 1

            db.add(
                AgentLog(
                    agent="discovery_agent",
                    action=f"found {company.name}",
                    detail=verdict.get("reason") or f"via {_domain(url)}",
                    company_id=company.id,
                )
            )
            await db.commit()

    db.add(
        AgentLog(
            agent="discovery_agent",
            action=f"discovery complete: {kept} kept, {dropped} filtered out",
            detail=f"{len(queries)} queries · niche: {', '.join(profile.target_industries or []) or 'any'}",
        )
    )
    await db.commit()

    return discovered
