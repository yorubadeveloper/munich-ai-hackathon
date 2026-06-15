---
estimated_steps: 12
estimated_files: 3
skills_used: []
---

# T04: Tested Metrics and Evaluator

Create test fixtures and comprehensive pytest tests.

1. Create `backend/tests/fixtures/eval_synthetic_sample.json` — a small static fixture (3-5 postings with ground truth).
2. Create `backend/tests/test_eval_metrics.py` with tests:
   - Exact match → F1 = 1.0
   - Partial overlap → 0 < F1 < 1
   - Zero overlap → F1 = 0.0
   - Empty/None inputs → F1 = 0.0
   - Per-label aggregation correctness
   - Mean F1 calculation
3. Create `backend/tests/test_eval_evaluator.py` with tests:
   - Mock Pioneer and Gemini responses, verify evaluator produces correct result structure.
   - Verify result schema matches expected JSON structure for S03 evidence events.

## Inputs

- `backend/eval/metrics.py`
- `backend/eval/evaluator.py`

## Expected Output

- `backend/tests/fixtures/eval_synthetic_sample.json`
- `backend/tests/test_eval_metrics.py`
- `backend/tests/test_eval_evaluator.py`

## Verification

cd backend && uv run pytest tests/test_eval_metrics.py tests/test_eval_evaluator.py -v
