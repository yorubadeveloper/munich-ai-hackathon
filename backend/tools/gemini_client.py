"""
Gemini client.
The model is also synchronous under the hood, so each call is offloaded to a
thread. All structured calls go through a defensive JSON extractor because LLMs
occasionally wrap output in markdown fences or add stray prose.
"""
import json
import re
import asyncio
import logging

import google.generativeai as genai

from config import settings

log = logging.getLogger(__name__)

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
Score how well this company fits this candidate. Return valid JSON only:
{{
  "score": 8.5,
  "reasoning": "one sentence explaining the score"
}}

Candidate: {profile}
Company: {company}
Score from 1-10. Be strict. 7+ means genuinely strong fit.
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
            f"Content: {r.get('content', '')[:500]}"
            for r in results[:8]
        ]
    )
    prompt = RESEARCH_SYNTHESIS_PROMPT.format(
        company_name=company_name, results=content
    )
    text = await _generate(prompt)
    return _extract_json(text)


async def score_fit(enriched: dict, profile) -> dict:
    prompt = FIT_SCORE_PROMPT.format(
        profile=(
            f"{profile.role} | {', '.join(profile.stack)} | "
            f"{profile.location} | dealbreakers: {profile.dealbreakers}"
        ),
        company=json.dumps(enriched),
    )
    text = await _generate(prompt)
    parsed = _extract_json(text)
    # Guarantee a numeric score so the orchestrator's comparison never crashes.
    if "score" not in parsed:
        parsed["score"] = 0
    return parsed


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
