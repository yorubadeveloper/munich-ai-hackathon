---
estimated_steps: 14
estimated_files: 2
skills_used: []
---

# T04: Add tests for approval endpoints and fal client failure modes

Why: We need to verify the new approval endpoints work correctly and that the fal client degrades gracefully.

Do:
1. In `backend/tests/test_dossier.py`, add tests:
   - `test_approve_company_success` — PATCH approve sets company.status='approved', creates EvidenceEvent, returns 200.
   - `test_reject_company_success` — PATCH reject sets company.status='rejected', creates EvidenceEvent, returns 200.
   - `test_approve_company_not_found` — returns 404 for non-existent company.
   Use the existing test patterns (mocker, ASGITransport, mock_db) from the existing `test_get_dossier_success`.
2. Create `backend/tests/test_fal.py` with tests:
   - `test_generate_visual_no_key` — when `settings.fal_key` is empty, returns None without making any API call.
   - `test_generate_visual_success` — mock `fal_client.submit` to return a URL, verify the returned dict has `image_url` and `prompt`.
   - `test_generate_visual_timeout` — mock `fal_client.submit` to raise an exception, verify returns None without crashing.
   Use `mocker.patch` against config settings and the fal_client library.
3. Ensure `backend/tests/conftest.py` has the existing fixtures available (already does).

Done when: `cd backend && uv run python -m pytest tests/test_dossier.py tests/test_fal.py -v` passes all tests.

## Inputs

- `backend/tests/test_dossier.py`
- `backend/tests/conftest.py`
- `backend/tests/fixtures/evidence.py`
- `backend/api/dossier.py`
- `backend/tools/fal_client.py`

## Expected Output

- `backend/tests/test_dossier.py`
- `backend/tests/test_fal.py`

## Verification

cd backend && uv run python -m pytest tests/test_fal.py -v --tb=short
