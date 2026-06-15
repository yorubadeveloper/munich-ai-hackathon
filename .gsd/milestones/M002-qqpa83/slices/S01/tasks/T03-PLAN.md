---
estimated_steps: 9
estimated_files: 1
skills_used: []
---

# T03: Implemented Token-Overlap Metrics

Create `backend/eval/evaluator.py` that orchestrates the evaluation pipeline.

The evaluator must:
1. Load synthetic data from `backend/eval/data/synthetic_eval.json` (or accept a path argument).
2. For each posting: extract entities via Pioneer (using existing `gliner_client.extract_job_entities`) and via Gemini (using the existing Gemini client or a new extraction prompt).
3. Compare both extractions against ground truth using `eval.metrics` functions.
4. Produce a structured result: `{per_label_f1_pioneer: {...}, per_label_f1_gemini: {...}, mean_f1_pioneer: float, mean_f1_gemini: float, sample_count: int, fine_tuning_triggered: bool}`.
5. Log per-label and mean F1 scores.
6. Include a CLI entry point for standalone runs.
7. The result schema must be stable — S03 will persist it as an evidence event.

## Inputs

- `backend/eval/generator.py`
- `backend/eval/metrics.py`
- `backend/tools/gliner_client.py`
- `backend/tools/gemini_client.py`

## Expected Output

- `backend/eval/evaluator.py`

## Verification

uv run python -c "from eval.evaluator import EvalResult; print('import ok')"
