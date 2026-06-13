"""
Gemini client.
The model is also synchronous under the hood, so each call is offloaded to a
thread. All structured calls go through a defensive JSON extractor because LLMs
occasionally wrap output in markdown fences or add stray prose.
"""
import asyncio
import json
import logging
import re

import google.generativeai as genai

from config import settings

log = logging.getLogger(__name__)

model = None
if settings.gemini_api_key:
    genai.configure(api_key=settings.gemini_api_key)
    model = genai.GenerativeModel(settings.gemini_model)


RESEARCH_SYNTHESIS_PROMPT = """
Given these web search results about {company_name}, extract a structured profile.
Return valid JSON only, no markdown:
{{
  "funding_stage": "Seed|Series A|Series B|Series C|Public|Unknown",
  "headcount": "1-10|10-50|50-200|200-500|500+|Unknown",
  "tech_stack": ["list", "of", "technologies"],
  "hiring_manager_name": "Name or null",
  "hiring_manager_linkedin": "LinkedIn URL or null",
  "hiring_manager_email": "email or null",
  "recent_news": "1-2 sentence summary of most relevant recent news",
  "company_summary": "1 sentence of what the company does"
}}

Search results:
{results}
"""

FIT_SCORE_PROMPT = """
You are a hiring-fit evaluator. Score how well this specific company fits
this specific candidate's criteria, from 1.0 to 10.0.

Candidate:
{profile}

Company:
{company}

Think step by step, then score. Scoring anchors (be decisive and use the FULL range):
- 9.0-10.0: Excellent. Perfect stack overlap, correct role, and strong target alignment.
- 7.0-8.9: Strong. Clear reason to talk, good tech-stack and role match.
- 5.0-6.9: Moderate. Plausible role/stack overlap, but some mismatch or unverified details.
- 1.0-4.9: Weak/No fit. Mismatch on role, stack, or explicitly listed dealbreakers.

CRITICAL WILDCARD RULES (Do not penalize unspecified preferences):
- If the candidate's target industries list is EMPTY, "any", or not specified,
  do NOT penalize the company for its industry. Treat it as a neutral/perfect match.
- If the candidate's target funding stages is EMPTY, "any", or not specified,
  do NOT penalize the company for its funding stage. Treat it as a neutral/perfect match.
- If the candidate's target company size is EMPTY, "any", or not specified,
  do NOT penalize the company for its size. Treat it as a neutral/perfect match.
- If any targeting field is unspecified, the score should be driven PURELY by how
  well the role matches (e.g. Software Engineer) and how well the tech stack
  overlaps (e.g. Python, Javascript). A great tech-stack + role match with no
  unspecified targeting limits should score 8.5 to 9.5 easily.

Scoring deductions (only apply if the candidate has EXPLICITLY specified a preference):
- Only deduct for industry mismatch if the candidate has listed target industries AND the company clearly violates them.
- Only deduct for funding stage mismatch if the candidate has listed target funding stages AND the company clearly violates them.
- Only deduct for company size mismatch if the candidate has listed a company size range AND the company clearly violates it.
- Only trigger a dealbreaker penalty (hard-cap at 2.0) if the SPECIFIC role being evaluated for the candidate (e.g. Software Engineer) violates a dealbreaker (e.g. the role itself is unpaid, or the role itself is an internship). Do NOT penalize the company just because they have hired interns, part-time staff, or other roles in unrelated departments.

Return valid JSON only, in this exact order (reasoning first, then the number):
{{
  "reasoning": "2-3 short clauses citing the specific criteria that matched or failed",
  "score": <number between 1.0 and 10.0>
}}
"""


RELEVANCE_GATE_PROMPT = """
You are filtering raw web search results during a job hunt. Decide if THIS result
is a real, on-target opportunity worth researching, or noise to discard.

Discard (relevant=false) if the result is any of:
- a listicle / roundup ("10 best startups hiring...", "top companies in...")
- a job-board aggregator category or search page, not a specific company/role
- a generic directory, wiki, news article, or blog not tied to one hiring company
- clearly outside the candidate's target industry, location, or seniority
- not actually about an open role or a specific company that hires

Keep (relevant=true) ONLY if BOTH are true:
1. The result is about ONE specific named company (not a job board, not a list).
2. You can name that company confidently from the title or content.

If you cannot confidently name a single company, set relevant=false and
company_name=null. A page titled like "Remote X Developer Jobs", "Top N startups",
"X jobs in 2026", or any multi-company listing is NOT relevant.

Candidate target:
{target}

Result:
- Title: {title}
- URL: {url}
- Content: {content}

Return valid JSON only:
{{
  "relevant": true,
  "company_name": "the single company's clean name, or null if not identifiable",
  "reason": "short reason"
}}
"""



def _extract_json(text: str) -> dict:
    """Best-effort JSON extraction from an LLM response."""
    if not text:
        return {}
    cleaned = text.strip()
    # Strip markdown code fences if present.
    cleaned = re.sub(r"^```(?:json)?", "", cleaned).strip()
    cleaned = re.sub(r"```$", "", cleaned).strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        # Fall back to grabbing the first {...} block.
        match = re.search(r"\{.*\}", cleaned, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                pass
    log.warning(f"Could not parse JSON from Gemini output: {text[:200]}")
    return {}


async def _generate(prompt: str) -> str:
    if model is None:
        log.warning("GEMINI_API_KEY not set - skipping Gemini generation.")
        return ""

    def _call() -> str:
        try:
            response = model.generate_content(prompt)
            return response.text or ""
        except Exception as e:
            log.warning(f"Gemini generate_content failed: {e}")
            return ""

    return await asyncio.to_thread(_call)


async def synthesise_research(company_name: str, results: list[dict]) -> dict:
    content = "\n\n".join(
        [
            f"Title: {r.get('title')}\nURL: {r.get('url')}\n"
            f"Content: {r.get('content', '') or r.get('raw_content', '')}"
            for r in results[:8]
        ]
    )
    prompt = RESEARCH_SYNTHESIS_PROMPT.format(
        company_name=company_name, results=content
    )
    text = await _generate(prompt)
    return _extract_json(text)


def _profile_summary(profile) -> str:
    """Compact, targeting-focused description of the candidate for prompts."""
    parts = [
        f"Role: {profile.role}",
        f"Seniority: {getattr(profile, 'seniority', '') or 'any'}",
        f"Stack: {', '.join(profile.stack)}",
        f"Location: {profile.location}",
        f"Remote pref: {getattr(profile, 'remote_pref', '') or 'any'}",
        f"Target industries: {', '.join(getattr(profile, 'target_industries', []) or []) or 'any'}",
        f"Target funding stages: {', '.join(getattr(profile, 'target_funding_stages', []) or []) or 'any'}",
        f"Target company size: {getattr(profile, 'company_size', '') or 'any'}",
        f"Dealbreakers: {', '.join(profile.dealbreakers or []) or 'none'}",
    ]
    return "\n".join(parts)


async def score_fit(enriched: dict, profile) -> dict:
    prompt = FIT_SCORE_PROMPT.format(
        profile=_profile_summary(profile),
        company=json.dumps(enriched),
    )
    text = await _generate(prompt)
    parsed = _extract_json(text)
    # Guarantee a numeric score so the orchestrator's comparison never crashes.
    if "score" not in parsed:
        parsed["score"] = 0
    return parsed


async def check_relevance(result: dict, profile) -> dict:
    """
    Fast discovery-time gate: is this raw search result a real, on-target lead?
    Returns {"relevant": bool, "company_name": str|None, "reason": str}.
    """
    target = (
        f"{getattr(profile, 'seniority', '') or ''} {profile.role}".strip()
        + f" | industries: {', '.join(getattr(profile, 'target_industries', []) or []) or 'any'}"
        + f" | location: {profile.location}"
        + f" | size: {getattr(profile, 'company_size', '') or 'any'}"
        + f" | stages: {', '.join(getattr(profile, 'target_funding_stages', []) or []) or 'any'}"
    )
    prompt = RELEVANCE_GATE_PROMPT.format(
        target=target,
        title=(result.get("title") or "")[:200],
        url=result.get("url") or "",
        content=(result.get("content") or "")[:800],
    )
    text = await _generate(prompt)
    parsed = _extract_json(text)
    if "relevant" not in parsed:
        # On parse failure, default to keeping it so we never silently drop
        # everything if the LLM hiccups; research stage will still gate by score.
        parsed = {"relevant": True, "company_name": None, "reason": "gate parse failed"}
    return parsed


PICK_CONTACT_PROMPT = """
You are choosing the single best person to send a cold/warm intro to at a company,
for a candidate who wants a {role} role there.

Prefer, in order: CTO, VP/Head of Engineering, technical co-founder/founder,
engineering manager, then technical recruiter. The person should plausibly
influence engineering hiring. Avoid sales, marketing, and unrelated roles.

Company: {company}
Candidates (LinkedIn people search results):
{candidates}

Return valid JSON only — the index of the best candidate (0-based) and why:
{{
  "index": 0,
  "reason": "short reason this is the right person"
}}
If none are appropriate, return {{"index": -1, "reason": "..."}}.
"""


async def pick_best_contact(company_name: str, role: str, candidates: list[dict]) -> dict:
    """Pick the best person to contact from LinkedIn search candidates."""
    if not candidates:
        return {}
    listing = "\n".join(
        f"{i}. {c.get('name')} — {c.get('role') or c.get('headline')} "
        f"({c.get('location') or 'location unknown'})"
        for i, c in enumerate(candidates)
    )
    prompt = PICK_CONTACT_PROMPT.format(
        role=role, company=company_name, candidates=listing
    )
    parsed = _extract_json(await _generate(prompt))
    idx = parsed.get("index", -1)
    try:
        idx = int(idx)
    except (TypeError, ValueError):
        idx = -1
    if 0 <= idx < len(candidates):
        chosen = dict(candidates[idx])
        chosen["pick_reason"] = parsed.get("reason", "")
        return chosen
    return {}


async def draft_outreach_message(prompt: str) -> dict:
    text = await _generate(prompt)
    return _extract_json(text)


async def draft_followup_message(company, message) -> str:
    prompt = f"""
Write a short follow-up message (max 60 words) for a job outreach that got no reply after 5 days.
Company: {company.name}
Original channel: {message.channel}
Keep it light, no guilt-tripping, genuine curiosity only.
Return the message text only, no JSON.
"""
    text = await _generate(prompt)
    return text.strip()
