# S01: Synthetic Data Generation and F1 Evaluation Engine

**Goal:** Build the evaluation engine: synthetic data generation via Gemini Structured Outputs, dual extraction (Pioneer + Gemini), and token-overlap F1 metric calculation — all verified by pytest.
**Demo:** After this, running the generator script produces 30-50 synthetic job postings as JSON, and the evaluator computes per-label F1 scores comparing Pioneer vs Gemini extraction. Pytest proves F1 calculation correctness with static fixtures.

## Must-Haves

- 1. backend/eval/generator.py produces 30-50 synthetic job postings as JSON files\n2. backend/eval/evaluator.py computes per-label token-overlap F1 scores\n3. Pytest suite with static JSON fixtures validates F1 calculation for exact, partial, and zero-overlap cases\n4. String normalization (lowercase, strip punctuation) applied before overlap calculation

## Proof Level

- This slice proves: pytest with static fixtures

## Integration Closure

Evaluation output JSON schema matches what S03 will persist as pioneer-eval evidence events

## Verification

- Logging of per-label F1 scores and overall mean F1 to stdout during eval runs

## Tasks

- [ ] **T01: Create synthetic data generator** `est:30min`
  Create `backend/eval/__init__.py` and `backend/eval/generator.py`.
  - Files: `backend/eval/__init__.py`, `backend/eval/generator.py`
  - Verify: uv run python -c "from eval.generator import SyntheticJobPosting; print('import ok')"

- [ ] **T02: Implement F1 metric calculation module** `est:20min`
  Create `backend/eval/metrics.py` with token-overlap F1 score calculation.
  - Files: `backend/eval/metrics.py`
  - Verify: uv run python -c "from eval.metrics import token_overlap_f1; assert token_overlap_f1('hello world', 'hello world') == 1.0; print('ok')"

- [ ] **T03: Build evaluator script with dual extraction and scoring** `est:30min`
  Create `backend/eval/evaluator.py` that orchestrates the evaluation pipeline.
  - Files: `backend/eval/evaluator.py`
  - Verify: uv run python -c "from eval.evaluator import EvalResult; print('import ok')"

- [ ] **T04: Create static test fixtures and pytest suite** `est:25min`
  Create test fixtures and comprehensive pytest tests.
  - Files: `backend/tests/fixtures/eval_synthetic_sample.json`, `backend/tests/test_eval_metrics.py`, `backend/tests/test_eval_evaluator.py`
  - Verify: cd backend && uv run pytest tests/test_eval_metrics.py tests/test_eval_evaluator.py -v

## Files Likely Touched

- backend/eval/__init__.py
- backend/eval/generator.py
- backend/eval/metrics.py
- backend/eval/evaluator.py
- backend/tests/fixtures/eval_synthetic_sample.json
- backend/tests/test_eval_metrics.py
- backend/tests/test_eval_evaluator.py
