---
estimated_steps: 6
estimated_files: 7
skills_used: []
---

# T04: Full Backend Test Suite Regression Check

**Why:** After T01's test additions, we must confirm no regressions across all backend tests — including the fal, evidence, and Tavily client tests established in S01–S04.

**Do:**
1. Run the complete backend test suite: `uv run pytest` from `backend/`.
2. If any test fails, diagnose and fix the root cause (likely import path or fixture issues).
3. Document the final pass count.

**Done-when:** `uv run pytest` exits 0 with all tests passing.

## Inputs

- `backend/tests/test_dossier.py`
- `backend/tests/test_fal.py`
- `backend/tests/test_fal_client.py`
- `backend/tests/test_evidence.py`
- `backend/tests/test_tavily_client.py`
- `backend/tests/test_safe_http.py`
- `backend/tests/conftest.py`

## Expected Output

- Update the implementation and proof artifacts needed for this task.

## Verification

cd backend && uv run pytest -v
