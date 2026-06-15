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

from config import settings
from tools.safe_http import safe_async_client, validate_https_url

log = logging.getLogger(__name__)

PIONEER_INFERENCE_URL = validate_https_url("https://api.pioneer.ai/inference", {"api.pioneer.ai"})

# Circuit breaker: once Pioneer rejects us for auth/billing reasons (401/403),
# that will not change mid-run, so we stop calling it to avoid log spam and
# wasted requests on every discovered result.
_disabled_reason: str | None = None

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

    Pioneer's encoder response looks like:
        {
          "type": "encoder",
          "result": {
            "data": {
              "entities": {
                "organization": [{"text": "Apple", "confidence": 1.0, ...}],
                "product": [{"text": "iPhone", ...}]
              }
            }
          }
        }
    We defensively unwrap result/data and also handle a couple of alternate
    shapes (top-level entities, or list-of-{label,text}).
    """
    # Unwrap result -> data if present.
    container = payload
    if isinstance(container.get("result"), dict):
        container = container["result"]
    if isinstance(container.get("data"), dict):
        container = container["data"]

    entities = container.get("entities")
    if entities is None:
        # Last-ditch: some shapes nest under output.
        inner = payload.get("output")
        if isinstance(inner, dict):
            entities = inner.get("entities")

    result: dict = {}

    if isinstance(entities, dict):
        # {label: [{text, confidence, ...}], ...}  (Pioneer's actual shape)
        for label, vals in entities.items():
            if isinstance(vals, list) and vals:
                first = vals[0]
                if isinstance(first, dict):
                    val = first.get("text") or first.get("value")
                else:
                    val = first
                if val:
                    result[label] = val
            elif isinstance(vals, str) and vals:
                result[label] = vals
    elif isinstance(entities, list):
        # [{label/type, text/value}, ...]
        for e in entities:
            if not isinstance(e, dict):
                continue
            label = e.get("label") or e.get("type")
            text = e.get("text") or e.get("value")
            if label and text and label not in result:
                result[label] = text

    return result


async def submit_training_job(training_data: list[dict]) -> tuple[str, str | None, str | None]:
    """
    Submits a training job to Pioneer.
    Handles errors gracefully to support degradation.
    Returns: (status, job_id, error_reason)
    """
    if not settings.pioneer_api_key:
        log.warning("No Pioneer API key configured. Skipping training.")
        return "unavailable", None, "No API key configured"

    url = validate_https_url("https://api.pioneer.ai/v1/training", {"api.pioneer.ai"})
    try:
        async with safe_async_client(allowed_hosts={"api.pioneer.ai"}) as client:
            response = await client.post(
                url,
                headers={
                    "X-API-Key": settings.pioneer_api_key,
                    "Content-Type": "application/json",
                },
                json={
                    "model": "fastino/gliner2-base-v1",
                    "training_data": training_data,
                },
                timeout=60,
            )

            if response.status_code >= 400:
                reason = f"Pioneer training failed ({response.status_code}): {response.text[:200]}"
                log.warning(reason)
                return "failed", None, reason

            data = response.json()
            job_id = data.get("id") or data.get("job_id")
            if not job_id:
                return "failed", None, "API returned success but no job ID"

            return "submitted", str(job_id), None

    except Exception as e:
        reason = f"Pioneer training submission failed: {e}"
        log.warning(reason)
        return "failed", None, reason

async def extract_job_entities(text: str) -> dict:
    global _disabled_reason

    if not text:
        return {}
    if not settings.pioneer_api_key or not settings.pioneer_model_id:
        # Not configured — orchestrator handles the empty result gracefully.
        return {}
    if _disabled_reason:
        # Already known to be unavailable this run; skip silently.
        return {}

    try:
        async with safe_async_client(allowed_hosts={"api.pioneer.ai"}) as client:
            response = await client.post(
                PIONEER_INFERENCE_URL,
                headers={
                    "X-API-Key": settings.pioneer_api_key,
                    "Content-Type": "application/json",
                },
                json={
                    "model_id": settings.pioneer_model_id,
                    "text": text,
                    "schema": {"entities": JOB_ENTITY_LABELS},
                    "threshold": 0.5,
                },
                timeout=30,
            )
            if response.status_code in (401, 402, 403):
                # Auth/billing problem — won't recover mid-run. Trip the breaker
                # and log it once so discovery stops hammering Pioneer.
                _disabled_reason = f"{response.status_code} {response.text[:200]}"
                log.warning(
                    "Pioneer GLiNER disabled for this run "
                    f"({response.status_code}). Falling back to non-GLiNER "
                    f"extraction. Detail: {response.text[:200]}"
                )
                return {}
            if response.status_code >= 400:
                log.warning(f"Pioneer inference failed ({response.status_code}): {response.text[:300]}")
                return {}
            return _parse_entities(response.json())
    except Exception as e:
        log.warning(f"Pioneer GLiNER extraction failed: {e}")
        return {}
