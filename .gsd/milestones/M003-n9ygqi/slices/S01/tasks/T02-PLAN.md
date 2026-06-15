---
estimated_steps: 1
estimated_files: 1
skills_used: []
---

# T02: Write mocked fal client tests

Write mocked pytest tests in `backend/tests/test_fal_client.py` to validate successful generation, timeout behavior, and empty API key fallback.

## Inputs

- `backend/tools/fal_client.py`

## Expected Output

- `backend/tests/test_fal_client.py`

## Verification

`uv run pytest backend/tests/test_fal_client.py`

## Observability Impact

Test suite output includes fal client validation.
