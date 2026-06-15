# S02: Pioneer Training Integration and Conditional Fine-Tuning

**Goal:** Extend gliner_client.py with training/evaluation endpoints, implement conditional fine-tuning trigger logic in the evaluator, and ensure graceful degradation on API failure.
**Demo:** After this, the evaluator conditionally triggers Pioneer fine-tuning when mean F1 < 80%. If the training API is unavailable, the pipeline logs the failure and continues with base model results. Pytest proves the conditional logic and graceful degradation.

## Must-Haves

- 1. gliner_client.py supports POST to /felix/training-jobs and /felix/evaluations endpoints\n2. Conditional fine-tuning triggers when mean F1 < 80% with a separate ~100 item training batch generated\n3. Training API failures are caught and logged without crashing\n4. Pytest verifies conditional trigger logic and graceful degradation\n5. Pioneer training host added to safe_http allow-list

## Proof Level

- This slice proves: pytest with mocked HTTP responses

## Integration Closure

Fine-tuning results (or skip reason) included in the evaluation output structure consumed by S03

## Verification

- Log messages for fine-tuning trigger, job submission, and failure fallback

## Tasks

- [ ] **T01: Extend gliner_client with training and evaluation endpoints** `est:20min`
  Extend `backend/tools/gliner_client.py` with two new async functions:
  - Files: `backend/tools/gliner_client.py`
  - Verify: uv run python -c "from tools.gliner_client import submit_training_job, submit_evaluation; print('import ok')"

- [ ] **T02: Implement conditional fine-tuning trigger with graceful degradation** `est:25min`
  Add conditional fine-tuning logic to `backend/eval/evaluator.py`:
  - Files: `backend/eval/evaluator.py`, `backend/eval/generator.py`
  - Verify: uv run python -c "from eval.evaluator import EvalResult; r = EvalResult.__fields__; assert 'fine_tuning_triggered' in r; print('ok')"

- [ ] **T03: Pytest suite for fine-tuning trigger and graceful degradation** `est:25min`
  Create `backend/tests/test_eval_finetuning.py` with comprehensive tests:
  - Files: `backend/tests/test_eval_finetuning.py`
  - Verify: cd backend && uv run pytest tests/test_eval_finetuning.py -v

## Files Likely Touched

- backend/tools/gliner_client.py
- backend/eval/evaluator.py
- backend/eval/generator.py
- backend/tests/test_eval_finetuning.py
