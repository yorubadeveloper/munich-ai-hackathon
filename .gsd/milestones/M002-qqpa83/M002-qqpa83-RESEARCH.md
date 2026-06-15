# M002-qqpa83: Pioneer Evaluation and Model Quality — Research

**Date:** 2026-06-15

## Summary

This milestone focuses on evaluating and improving the Pioneer/GLiNER2 entity extraction pipeline. We currently use Pioneer via an asynchronous client (`backend/tools/gliner_client.py`) with a fixed set of seven entity labels: `company_name`, `job_title`, `tech_stack`, `company_stage`, `hiring_manager`, `salary`, and `remote_policy`. The goal is to build a structured evaluation framework that compares Pioneer's performance against Gemini (as a gold standard) on synthetic job postings, with the ability to trigger conditional fine-tuning if performance is suboptimal.

The research confirms that Pioneer provides a specialized API for both evaluation and training (fine-tuning). We will leverage these endpoints to automate the feedback loop. Evaluation results will be persisted in PostgreSQL as `evidence_events` with an `artifact_type` of `pioneer-eval`, which will then be visualized on the frontend using Recharts.

## Recommendation

We should build a standalone evaluation module under `backend/eval/` that handles synthetic data generation, metric calculation, and training job management. By separating these concerns from the main orchestrator, we ensure the evaluation pipeline is robust, testable, and non-blocking for real-time extraction. We will use Gemini with Structured Outputs to generate high-fidelity synthetic data, and implement a custom F1 score calculation for token-overlap metrics to allow for local validation before hitting the Pioneer Eval API.

## Implementation Landscape

### Key Files

- `backend/tools/gliner_client.py` — Current Pioneer client; needs expansion to support training and evaluation endpoints.
- `backend/tools/gemini_client.py` — Gemini client; will be used for synthetic data generation using Structured Outputs.
- `backend/models.py` — Contains `EvidenceEvent` schema; no changes needed as it already supports generic JSON payloads.
- `frontend/components/ResourceChartInner.tsx` — Current Recharts implementation; needs a new branch to render `pioneer-eval` comparison data (likely a BarChart or RadarChart showing per-label F1 scores).
- `backend/eval/generator.py` (New) — Script to generate 30-50 synthetic Tech/Startup job postings via Gemini.
- `backend/eval/evaluator.py` (New) — Script to compute F1 scores, trigger fine-tuning, and save results to Postgres.

### Build Order

1. **Synthetic Data Generation:** Build `generator.py` to create the ground truth dataset. This unblocks all subsequent evaluation work.
2. **Metric Calculation (Local):** Implement F1 score logic in `evaluator.py` and verify with pytest against mock datasets.
3. **Pioneer Training/Eval Integration:** Update `gliner_client.py` to support `/felix/training-jobs` and `/felix/evaluations`.
4. **Postgres & UI Persistence:** Implement the bridge that saves `evaluator.py` results to the database and updates the React frontend.

### Verification Approach

- **Unit Tests:** `backend/tests/test_eval_metrics.py` to verify F1 calculation.
- **Integration Tests:** Run `generator.py` and confirm JSON output format; run `evaluator.py` with mock responses to verify DB writes.
- **Visual Verification:** Inspect the company dossier in the Next.js UI to confirm the Recharts chart displays correctly for a `pioneer-eval` event.

## Constraints

- **Safe HTTP Targets:** Any new Pioneer or Gemini endpoints must be added to the allow-list in `backend/tools/safe_http.py`.
- **Async DB Access:** All database interactions in the evaluation scripts must use `SQLAlchemy` async sessions.

## Common Pitfalls

- **Token Overlap Complexity:** NER evaluation can be tricky with partial matches. We should normalize strings (lowercase, strip punctuation) before calculating overlap to avoid fragile metrics.
- **Fine-Tuning Latency:** Training jobs are asynchronous and take time. The evaluation script should handle "job pending" states gracefully and not block the pipeline.

## Open Risks

- **API Token Usage:** Generating large synthetic datasets and running training jobs could consume Gemini/Pioneer credits quickly. We should keep the default batch sizes conservative (30-50 for eval, 100 for train).
- **Pioneer Training Availability:** If the `/felix/training-jobs` endpoint is flaky during the hackathon, we must ensure the `evaluator.py` has a robust "skip and log" fallback.
