---
estimated_steps: 10
estimated_files: 2
skills_used: []
---

# T02: Implemented Conditional Trigger Logic

Add conditional fine-tuning logic to `backend/eval/evaluator.py`:

1. After computing mean F1, check if `mean_f1_pioneer < 0.80`.
2. If below threshold:
   a. Generate a separate ~100-item training batch using `eval.generator` (distinct from the eval set).
   b. Call `gliner_client.submit_training_job()` with the training data.
   c. If training submission succeeds, record `fine_tuning_triggered: True, training_job_id: ...` in the result.
   d. If training submission fails, record `fine_tuning_triggered: True, fine_tuning_error: '...'` and log the error.
3. If mean F1 >= 0.80, record `fine_tuning_triggered: False`.
4. The evaluator must never raise an exception from fine-tuning failures.
5. Update the `EvalResult` schema to include fine-tuning fields.

## Inputs

- `backend/eval/evaluator.py`
- `backend/tools/gliner_client.py`

## Expected Output

- `backend/eval/evaluator.py`

## Verification

uv run python -c "from eval.evaluator import EvalResult; r = EvalResult.__fields__; assert 'fine_tuning_triggered' in r; print('ok')"
