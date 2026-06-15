---
estimated_steps: 10
estimated_files: 2
skills_used: []
---

# T01: Persisted Evaluation Results as EvidenceEvents

Create `backend/eval/persist.py` with a `persist_eval_results` function:

1. Accept the eval result dict and a `company_id` (UUID).
2. Create an `EvidenceEvent` with:
   - `resource_name`: 'pioneer'
   - `artifact_type`: 'pioneer-eval'
   - `status`: 'success'
   - `payload`: the full eval result dict (per_label_f1_pioneer, per_label_f1_gemini, mean_f1_pioneer, mean_f1_gemini, sample_count, fine_tuning_triggered, etc.)
3. Use async SQLAlchemy session via `database.get_db()`.
4. Ensure no secrets (API keys) are included in the payload.
5. Add a pytest test in `backend/tests/test_eval_persist.py` that mocks the DB session and verifies the EvidenceEvent fields.

## Inputs

- `backend/models.py`
- `backend/database.py`

## Expected Output

- `backend/eval/persist.py`
- `backend/tests/test_eval_persist.py`

## Verification

cd backend && uv run pytest tests/test_eval_persist.py -v
