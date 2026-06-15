---
id: S02
milestone: M002-qqpa83
status: ready
---

# S02: Pioneer Training Integration and Conditional Fine-Tuning — Context

<!-- Slice-scoped context. Milestone-only sections (acceptance criteria, completion class,
     milestone sequence) do not belong here — those live in the milestone context. -->

## Goal

Add conditional Pioneer fine-tuning that automatically responds to low S01 mean F1, generates a targeted training batch, submits training safely, and leaves auditable local lifecycle artifacts for downstream persistence and display.

## Why this Slice

S01 establishes the local evaluation baseline; S02 turns that baseline into adaptive Pioneer behavior by triggering fine-tuning when measured quality falls below the 80% threshold, and it produces the training lifecycle evidence that S03 will later persist and visualize in the company dossier.

## Scope

### In Scope

- Read the S01 evaluation outputs, including mean F1, per-label F1, base-model metrics, and local artifact paths.
- Automatically trigger fine-tuning when mean F1 is below 80%.
- Preserve a clear trigger decision showing the mean F1, threshold, and whether fine-tuning was triggered or skipped.
- Generate a separate approximately 100 item training batch when fine-tuning is triggered.
- Make the training batch weak-label focused by over-sampling labels with the lowest F1 scores from S01, so the tuning attempt visibly responds to measured extraction gaps.
- Submit the training job to Pioneer when the threshold condition is met and credentials/API availability allow it.
- Treat Pioneer training as asynchronous: submit and record returned status/job id when available, but do not block the demo path waiting for full training completion.
- Continue with base-model evaluation results when training submission fails, is unavailable, is pending, or returns an error.
- Write explicit degraded lifecycle status for failure or unavailable states, including safe error summaries, reason codes, timestamps, and confirmation that base-model metrics were preserved.
- Produce local S03-ready lifecycle JSON describing trigger decision, training batch path, training status, job id if present, degraded reason if present, and preserved base metrics.
- Add pytest coverage for conditional trigger logic, training-batch generation behavior, and graceful degradation around mocked Pioneer training failures.

### Out of Scope

- Proving that the fine-tuned model improves extraction quality; S02 only needs submission/fallback proof, not completed post-training metrics.
- Blocking until Pioneer training completes.
- Re-running evaluation against a fine-tuned model as a required success condition.
- Writing lifecycle evidence to PostgreSQL; S03 owns database persistence.
- Rendering fine-tuning status or metric charts in the Next.js company dossier; S03 owns UI delivery.
- Expanding beyond the current seven labels: `company_name`, `job_title`, `tech_stack`, `company_stage`, `hiring_manager`, `salary`, and `remote_policy`.
- Logging secrets, raw authorization headers, or sensitive API request metadata.

## Constraints

- S02 depends on S01 local evaluation artifacts and should not duplicate S01 metric calculation work except as needed to read/validate prior outputs.
- Fine-tuning must follow the milestone decision for graceful degradation: Pioneer training failure must not crash or erase base-model evaluation results.
- The default behavior after a below-threshold mean F1 is automatic training submission, not an interactive prompt.
- API latency and asynchronous training must not make the evaluation pipeline feel stuck; submission proof is enough for this slice.
- Training batch generation should remain conservative around hackathon API credits: approximately 100 items, focused on weak labels rather than unbounded regeneration.
- Local artifacts must be safe for later demo/persistence use and must exclude secrets or raw sensitive API logs.
- Status details should be explicit enough for S03 to surface a truthful lifecycle state rather than silently hiding skipped or failed fine-tuning.

## Integration Points

### Consumes

- `backend/eval/` S01 evaluation artifacts — Provides mean F1, per-label F1, base metrics, and paths to generated evaluation data.
- `backend/tools/gliner_client.py` — Pioneer/GLiNER2 client to extend or call for training-job submission.
- `backend/tools/gemini_client.py` — Gemini client or generator path used to create the weak-label-focused training batch.
- Current seven-label extraction contract — Defines which labels can be over-sampled and targeted during training batch generation.
- Static pytest fixtures and mocked Pioneer responses — Used to prove trigger logic and graceful degradation without live API calls.

### Produces

- Local training batch JSON — Approximately 100 synthetic examples focused on labels with the weakest S01 F1 scores.
- Local fine-tuning lifecycle JSON — S03-ready payload containing trigger decision, threshold, mean F1, training status, job id if returned, degraded reason if any, artifact paths, timestamps, and preserved base metrics.
- Safe run summary/log output — Human-readable explanation of whether fine-tuning was triggered, submitted, skipped, pending, or degraded.
- Tests for conditional fine-tuning — Pytest coverage for below-threshold trigger behavior, above-threshold skip behavior, weak-label batch focus, and training API failure fallback.

## Open Questions

- Exact lifecycle status vocabulary for training states such as `skipped_threshold_met`, `submitted`, `pending`, `failed`, and `unavailable` — current thinking: keep statuses explicit and stable enough for S03 to render without interpreting logs.
- Whether to add an optional dry-run flag for credit safety even though default behavior is automatic below threshold — current thinking: optional flag is acceptable only if it does not weaken the default demo path.
- Whether S02 should include a best-effort status refresh command for previously submitted jobs — current thinking: defer unless the Pioneer API makes this trivial and non-blocking.
