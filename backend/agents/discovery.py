"""
Discovery Agent.
Think: user wants {role} at {location} startups — where do I search?
Act: Tavily search across job boards and company pages.
Observe: parse results, deduplicate, filter dealbreakers, write to DB.
"""
import logging

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from models import Company, UserProfile, AgentLog
from tools.tavily_client import search
from tools.gliner_client import extract_job_entities

log = logging.getLogger(__name__)

SOURCES = [
    '{role} "{location}" site:wellfound.com',
    '{role} "{stack}" startup hiring Munich Europe 2025',
    '{role} site:linkedin.com/jobs "{location}"',
    "who is hiring {role} {stack} Europe June 2025",
]


async def run(db: AsyncSession) -> list[Company]:
    profile_result = await db.execute(select(UserProfile).limit(1))
    profile = profile_result.scalar_one_or_none()
    if not profile:
        log.warning("No user profile found. Seed one first.")
        return []

    discovered = []

    for query_template in SOURCES:
        query = query_template.format(
            role=profile.role,
            location=profile.location,
            stack=", ".join(profile.stack[:3]),
        )

        results = await search(query, max_results=5)

        for r in results:
            # GLiNER2 (via Pioneer API): extract structured entities from raw job text.
            entities = await extract_job_entities(r.get("content", ""))

            # Dealbreaker check.
            raw_text = (r.get("content", "") + r.get("title", "")).lower()
            if any(d.lower() in raw_text for d in (profile.dealbreakers or [])):
                continue

            # Deduplication.
            url = r.get("url")
            if not url:
                continue
            existing = await db.execute(
                select(Company).where(Company.job_url == url)
            )
            if existing.scalar_one_or_none():
                continue

            company = Company(
                name=entities.get("company_name") or r.get("title", "Unknown")[:80],
                website=url,
                job_url=url,
                source=query_template.split(" ")[0],
                raw_job_text=(r.get("content", "") or "")[:4000],
                status="discovered",
            )
            db.add(company)
            await db.commit()
            await db.refresh(company)
            discovered.append(company)

            entry = AgentLog(
                agent="discovery_agent",
                action=f"found {company.name}",
                detail=f"via: {query[:60]}",
                company_id=company.id,
            )
            db.add(entry)
            await db.commit()

    return discovered
