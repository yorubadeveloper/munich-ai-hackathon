---
estimated_steps: 18
estimated_files: 4
skills_used: []
---

# T02: Create circuit-broken fal client and wire into research pipeline

Why: The hackathon requires a creative fal.ai integration. It must be non-blocking — missing credentials or API failures must never crash the pipeline.

Do:
1. Add `fal_key: str = ''` to `backend/config.py` Settings class.
2. Add `fal-client` to `backend/pyproject.toml` under `[project] dependencies`.
3. Create `backend/tools/fal_client.py` with:
   - An `async def generate_visual(company_name: str, summary: str) -> dict | None` function.
   - If `settings.fal_key` is empty, log a warning and return None immediately.
   - Use `fal_client` to call a stable image generation endpoint (e.g., `fal-ai/fast-sdxl` or `fal-ai/flux/schnell`) with a prompt like 'Abstract visualization representing {company_name}: {summary[:200]}. Modern, clean, corporate style.'
   - Wrap the entire call in a try/except with a 30-second timeout.
   - On success, return `{'image_url': result_url, 'prompt': prompt_used}`.
   - On any exception (timeout, auth, network), log the error and return None.
4. In `backend/agents/orchestrator.py`, after the `research.run()` call succeeds (when status transitions from 'discovered' to 'researched'), add a fire-and-forget background call:
   - Import `fal_client` from tools.
   - Call `fal_client.generate_visual(company.name, result.recent_news or '')` in a try/except.
   - If it returns a result dict, create an EvidenceEvent with resource_name='fal', artifact_type='visual_artifact', payload=result_dict, status='success'.
   - If it returns None or raises, create an EvidenceEvent with resource_name='fal', artifact_type='visual_artifact', payload={}, status='error', error_context={'reason': str(err)}.
   - Add and commit the evidence event. This must not block or crash the main pipeline.

Done when: `fal_client.py` exists with circuit-breaking, the orchestrator triggers it after research, and `uv run ruff check .` passes.

## Inputs

- `backend/config.py`
- `backend/agents/orchestrator.py`
- `backend/models.py`
- `backend/pyproject.toml`
- `backend/schemas/evidence.py`

## Expected Output

- `backend/tools/fal_client.py`
- `backend/config.py`
- `backend/pyproject.toml`
- `backend/agents/orchestrator.py`

## Verification

cd backend && uv run ruff check backend/tools/fal_client.py backend/config.py backend/agents/orchestrator.py
