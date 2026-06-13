"""
GLiNER2 entity extraction via the Pioneer inference API.

GLiNER2 runs on Pioneer's infrastructure (https://docs.pioneer.ai), not locally,
so there is no torch/transformers dependency here — just an HTTP call. We use the
native POST /inference endpoint with a schema of entity labels, which returns
deterministic structured output (no hallucinated/malformed JSON).

Fine-tune a GLiNER model on Pioneer, then set PIONEER_MODEL_ID to either a base
model id (e.g. "fastino/gliner2-base-v1") or your training job id (e.g.
"job_abc123"). If no key/model is configured, extraction is skipped gracefully
and the orchestrator falls back to other signals.
"""
import logging

import httpx

from config import settings

log = logging.getLogger(__name__)

PIONEER_INFERENCE_URL = "https://api.pioneer.ai/inference"

# Entity labels we want GLiNER2 to pull out of raw job-posting text.
JOB_ENTITY_LABELS = [
    "company_name",
    "job_title",
    "tech_stack",
    "company_stage",
    "hiring_manager",
    "salary",
    "remote_policy",
]


def _parse_entities(payload: dict) -> dict:
    """
    Normalize Pioneer's response into {label: first_text_value}.

    Pioneer returns extracted entities; shapes vary slightly by model/version, so
    we defensively handle the common forms (a list of {label,text} or a dict of
    label -> [values]).
    """
    result: dict = {}
    entities = payload.get("entities")

    # Some responses nest under "output" or "result".
    if entities is None:
        for key in ("output", "result", "data"):
            inner = payload.get(key)
            if isinstance(inner, dict) and "entities" in inner:
                entities = inner["entities"]
                break

    if isinstance(entities, list):
        for e in entities:
            if not isinstance(e, dict):
                continue
            label = e.get("label") or e.get("type")
            text = e.get("text") or e.get("value")
            if label and text and label not in result:
                result[label] = text
    elif isinstance(entities, dict):
        for label, vals in entities.items():
            if isinstance(vals, list) and vals:
                first = vals[0]
                result[label] = first.get("text") if isinstance(first, dict) else first
            elif isinstance(vals, str):
                result[label] = vals

    return result


async def extract_job_entities(text: str) -> dict:
    if not text:
        return {}
    if not settings.pioneer_api_key or not settings.pioneer_model_id:
        # Not configured — orchestrator handles the empty result gracefully.
        return {}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                PIONEER_INFERENCE_URL,
                headers={
                    "X-API-Key": settings.pioneer_api_key,
                    "Content-Type": "application/json",
                },
                json={
                    "model_id": settings.pioneer_model_id,
                    "text": text[:4000],
                    "schema": {"entities": JOB_ENTITY_LABELS},
                    "threshold": 0.5,
                },
                timeout=30,
            )
            if response.status_code >= 400:
                log.warning(
                    f"Pioneer inference failed "
                    f"({response.status_code}): {response.text[:300]}"
                )
                return {}
            return _parse_entities(response.json())
    except Exception as e:
        log.warning(f"Pioneer GLiNER extraction failed: {e}")
        return {}
