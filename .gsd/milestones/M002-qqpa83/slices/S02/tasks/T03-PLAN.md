---
estimated_steps: 12
estimated_files: 1
skills_used: []
---

# T03: Ensured Graceful Degradation on Failure

Create `backend/tests/test_eval_finetuning.py` with comprehensive tests:

1. Test fine-tuning triggered when mean F1 < 0.80:
   - Mock `gliner_client.submit_training_job` to return a job response.
   - Verify `fine_tuning_triggered: True` and `training_job_id` in result.
2. Test fine-tuning NOT triggered when mean F1 >= 0.80:
   - Verify `fine_tuning_triggered: False`.
3. Test graceful degradation on training API failure:
   - Mock `submit_training_job` to raise `httpx.HTTPStatusError` or return None.
   - Verify evaluator does not crash, `fine_tuning_error` field is populated.
4. Test graceful degradation when Pioneer API key is not configured:
   - Verify evaluator still produces results with extraction fallback.
5. Verify training batch generation produces ~100 items distinct from eval set.

## Inputs

- `backend/eval/evaluator.py`
- `backend/tools/gliner_client.py`

## Expected Output

- `backend/tests/test_eval_finetuning.py`

## Verification

cd backend && uv run pytest tests/test_eval_finetuning.py -v
