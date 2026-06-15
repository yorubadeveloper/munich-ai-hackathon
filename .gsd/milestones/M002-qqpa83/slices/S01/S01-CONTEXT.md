---
id: S01
milestone: M002-qqpa83
status: ready
---

# S01: Synthetic Data Generation and F1 Evaluation Engine — Context

<!-- Slice-scoped context. Milestone-only sections (acceptance criteria, completion class,
     milestone sequence) do not belong here — those live in the milestone context. -->

## Goal

Deliver a local, auditable synthetic Tech/Startup job-posting dataset and token-overlap F1 evaluation engine comparing Pioneer/GLiNER2 extraction against Gemini extraction.

## Why this Slice

This slice creates the measured dataset and metric foundation needed before S02 can make conditional fine-tuning decisions and before S03 can persist and visualize Pioneer evaluation evidence.

## Scope

### In Scope

- Generate 30–50 synthetic Tech/Startup job postings as local JSON artifacts.
- Prioritize a messy realistic mix of job postings, including incomplete salary details, vague company stages, mixed remote-policy wording, noisy prose, and occasionally absent hiring-manager details.
- Store structured labels with each synthetic item for auditability, including explicit `null`/empty values when labels such as `salary` or `hiring_manager` are genuinely absent.
- Run Pioneer/GLiNER2 and Gemini extraction for the generated postings and produce local comparison artifacts.
- Compute token-overlap F1 with normalized forgiving matching: lowercase, strip punctuation, tokenize values, and reward partial overlap.
- Treat Gemini extraction output as the main reference for S01 Pioneer-vs-Gemini F1 scoring.
- Preserve synthetic ground-truth labels as audit context and use them to flag reference caveats when Gemini misses or mangles a label that the generated labels say is present.
- Produce a judge-readable local metrics summary containing per-label F1, macro mean, evaluated item counts, skipped/degraded reasons, and representative mismatch examples.
- Continue with warnings when generation or extraction partially succeeds, writing degraded status and skipped counts.
- Require at least 30 usable evaluated items before marking metrics credible; below that threshold, artifacts may be written for debugging but the credible run should fail or be clearly marked non-credible.
- Add pytest coverage proving F1 calculation correctness with static fixtures.

### Out of Scope

- Triggering Pioneer fine-tuning or generating the separate training batch; S02 owns this work.
- Writing `pioneer-eval` evidence events to PostgreSQL; S03 owns persistence.
- Rendering the Recharts comparison chart in the Next.js company dossier; S03 owns UI delivery.
- Expanding beyond the current seven labels: `company_name`, `job_title`, `tech_stack`, `company_stage`, `hiring_manager`, `salary`, and `remote_policy`.
- Manual curation of the synthetic dataset beyond generated fixtures and local audit artifacts.
- Sending outreach, changing approval flow, or touching delivery integrations.

## Constraints

- Scripts should live under the backend evaluation area and run through the local backend workflow using `uv run`.
- Local artifacts must be inspectable without requiring the frontend UI.
- No secrets, raw API tokens, or sensitive request headers may be logged or stored in generated artifacts.
- Partial API failures must be explicit in the summary rather than silently hidden.
- S01 should stop at local artifacts and metrics so later slices keep clear ownership of fine-tuning, persistence, and visualization.
- The F1 implementation should be deterministic and covered by static pytest fixtures.
- Generated data should be realistic enough for judge-facing credibility, not only perfectly formatted happy-path examples.

## Integration Points

### Consumes

- `backend/tools/gliner_client.py` — Pioneer/GLiNER2 extraction client used to obtain model outputs for comparison.
- `backend/tools/gemini_client.py` — Gemini client used for synthetic job-post generation and Gemini extraction reference output.
- Current seven-label extraction contract — Defines the labels S01 generates, extracts, compares, and reports.
- Static pytest fixtures — Provide deterministic examples for validating token-overlap F1 behavior without live API calls.

### Produces

- `backend/eval/` evaluation modules/scripts — Local generation, extraction-comparison, and metric calculation code for this slice.
- Local synthetic dataset JSON — 30–50 generated Tech/Startup job postings with auditable structured labels and explicit absent-label representation.
- Local extraction comparison JSON — Pioneer and Gemini outputs per evaluated posting, plus skipped/degraded metadata where applicable.
- Local metrics summary — Judge-readable per-label F1, macro mean, counts, degraded reasons, representative mismatches, and Gemini-reference caveats.
- Pytest coverage for metric calculation — Static fixture tests proving normalized token-overlap F1 correctness.

## Open Questions

- Whether S01 should emit a future-compatible local `pioneer-eval` payload shape even though S03 owns database persistence and chart rendering — current thinking: optional only if it does not expand scope or couple S01 to the UI schema.
