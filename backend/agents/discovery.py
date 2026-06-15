"""
Discovery Agent.
Think: given the candidate's niche, stage, size, and geography preferences,
       what precise searches surface REAL, on-target open roles?
Act: Tavily search across job boards and company pages using profile-driven queries.
Observe: run an LLM relevance gate to drop listicles/aggregators/off-target noise,
         clean up the company name, deduplicate, then write to DB.
"""

import logging
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import AgentLog, Company, UserProfile
from tools.gemini_client import check_relevance
from tools.gliner_client import extract_job_entities
from tools.tavily_client import search

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
    # More job boards / aggregators / listing sites.
    "remoteok.com",
    "remoteok.io",
    "weworkremotely.com",
    "remote.co",
    "remotive.com",
    "remotive.io",
    "stackoverflow.com",
    "dice.com",
    "wellfound.com/jobs",
    "angellist.com",
    "lensa.com",
    "jobspresso.co",
    "flexjobs.com",
    "workingnomads.com",
    "nodesk.co",
    "authenticjobs.com",
    "jobgether.com",
    "himalayas.app",
    "otta.com",
    "levels.fyi",
    "talent.io",
    "honeypot.io",
    "arc.dev",
    "turing.com",
    "toptal.com",
    "upwork.com",
    "freelancer.com",
    "naukri.com",
    "totaljobs.com",
    "reed.co.uk",
    "stepstone.de",
    "xing.com",
    "kununu.com",
    "joblift.com",
    "adzuna.com",
    "jora.com",
    "snaphunt.com",
    "wantedly.com",
    "f6s.com",
}

# Title/URL patterns that indicate a listing/roundup page, not a single company.
_LISTING_PATTERNS = [
    "jobs in",
    "jobs at",
    "remote jobs",
    " jobs ",
    "job openings",
    "open positions",
    "hiring now",
    "top ",
    "best ",
    "10 ",
    "20 ",
    "list of",
    "companies hiring",
    "who is hiring",
    "career page",
    "careers page",
    "job board",
    "vacancies",
    "find jobs",
    "browse jobs",
]


def _registry_year() -> int:
    return datetime.now(timezone.utc).year


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
    queries.append(f'"{role_phrase}" {industry_clause} "{location}" site:wellfound.com'.strip())

    # 2. Greenhouse boards — company ATS pages = real openings.
    queries.append(f'"{role_phrase}" {industry_clause} {stack} "{location}" site:boards.greenhouse.io'.strip())

    # 3. Lever boards — same idea, different ATS.
    queries.append(f'"{role_phrase}" {industry_clause} "{location}" site:jobs.lever.co'.strip())

    # 4. "Who is hiring" style, scoped to industry + stage + now.
    queries.append(f"{industry_clause} {stage_clause} startup hiring {role_phrase} {location} {year}".strip())

    # 5. Direct careers-page intent for the niche.
    queries.append(f'{industry_clause} {size} startup "{role_phrase}" careers "{location}" {year}'.strip())

    # Collapse whitespace and drop empties.
    return [" ".join(q.split()) for q in queries if q.strip()]


def _domain(url: str) -> str:
    d = (url or "").replace("https://", "").replace("http://", "").replace("www.", "").split("/")[0].lower()
    return d


def _is_aggregator(url: str) -> bool:
    d = _domain(url)
    if any(d == agg or d.endswith("." + agg) for agg in AGGREGATOR_DOMAINS):
        return True
    # Also catch aggregator path fragments (e.g. wellfound.com/jobs/...).
    low = (url or "").lower()
    return any(agg in low for agg in AGGREGATOR_DOMAINS if "/" in agg)


def _looks_like_listing(title: str, url: str) -> bool:
    """Heuristic: does the title/URL look like a jobs-listing/roundup page?"""
    hay = f" {(title or '').lower()} "
    if any(p in hay for p in _LISTING_PATTERNS):
        return True
    # URL slugs like /remote-azure-developer-jobs or /jobs/ are listings.
    slug = (url or "").lower()
    if "/jobs/" in slug or slug.rstrip("/").endswith("/jobs") or "-jobs" in slug:
        return True
    return False


def _looks_like_company_name(name: str) -> bool:
    """Reject names that are clearly page titles, not companies."""
    if not name:
        return False
    n = name.strip()
    if len(n) < 2 or len(n) > 60:
        return False
    low = f" {n.lower()} "
    if any(p in low for p in _LISTING_PATTERNS):
        return False
    # A real company name is usually short (1-5 words). Listing titles are long.
    if len(n.split()) > 6:
        return False
    return True


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

            # Drop listing/roundup pages by title/URL pattern (e.g.
            # "Remote Azure Developer Jobs in 2026", "/remote-...-jobs").
            if _looks_like_listing(r.get("title", ""), url):
                dropped += 1
                continue

            # Dealbreaker check (cheap, before any LLM call).
            raw_text = (r.get("content", "") + " " + r.get("title", "")).lower()
            if any(d.lower() in raw_text for d in (profile.dealbreakers or [])):
                dropped += 1
                continue

            # DB-level dedup.
            existing = await db.execute(select(Company).where(Company.job_url == url))
            if existing.scalar_one_or_none():
                continue

            # LLM relevance gate — the main quality lever.
            verdict = await check_relevance(r, profile)
            if not verdict.get("relevant", False):
                dropped += 1
                continue

            # GLiNER2 (Pioneer): deterministic structured extraction from the
            # raw job text — company, role, stack, stage, manager, salary, remote.
            entities = await extract_job_entities(r.get("content", ""))

            # Determine a REAL company name. We only accept names from the
            # relevance gate or GLiNER (both look at content), not the page
            # title. If we can't identify a real company, this is almost
            # certainly a listing page — drop it instead of inventing one.
            candidate_name = (verdict.get("company_name") or "").strip() or (entities.get("company_name") or "").strip()
            if not _looks_like_company_name(candidate_name):
                dropped += 1
                log.info(f"Dropped (no real company name): {r.get('title', '')[:60]}")
                continue
            name = candidate_name[:80]

            company = Company(
                name=name,
                website=url,
                job_url=url,
                source=_domain(url),
                raw_job_text=(r.get("content", "") or ""),
                status="discovered",
            )
            db.add(company)
            await db.commit()
            await db.refresh(company)
            discovered.append(company)
            kept += 1

            # Surface what GLiNER2 pulled out so the activity feed shows it working.
            gliner_bits = [f"{k}: {v}" for k, v in entities.items() if k != "company_name" and v]
            gliner_note = " · ".join(gliner_bits[:4]) if gliner_bits else None
            detail = gliner_note or verdict.get("reason") or f"via {_domain(url)}"

            db.add(
                AgentLog(
                    agent="discovery_agent",
                    action=f"found {company.name}",
                    detail=detail,
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
