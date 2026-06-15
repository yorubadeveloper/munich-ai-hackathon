---
estimated_steps: 11
estimated_files: 1
skills_used: []
---

# T01: Added Training Endpoints in GLiNER client

Extend `backend/tools/gliner_client.py` with two new async functions:

1. `async def submit_training_job(training_data: list[dict]) -> dict | None`:
   - POST to `https://api.pioneer.ai/felix/training-jobs` with the training data payload.
   - Return the job response (job_id, status) on success, or None on failure.
   - Handle 4xx/5xx responses gracefully: log warning and return None.
   - Use `safe_async_client(allowed_hosts={'api.pioneer.ai'})` (already allowed).

2. `async def submit_evaluation(eval_data: list[dict]) -> dict | None`:
   - POST to `https://api.pioneer.ai/felix/evaluations` with evaluation payload.
   - Same error handling pattern as training.

3. Ensure both functions check `settings.pioneer_api_key` and return None if not configured.
4. Add the X-API-Key header consistent with existing `extract_job_entities`.

## Inputs

- `backend/tools/gliner_client.py`
- `backend/tools/safe_http.py`
- `backend/config.py`

## Expected Output

- `backend/tools/gliner_client.py`

## Verification

uv run python -c "from tools.gliner_client import submit_training_job, submit_evaluation; print('import ok')"
