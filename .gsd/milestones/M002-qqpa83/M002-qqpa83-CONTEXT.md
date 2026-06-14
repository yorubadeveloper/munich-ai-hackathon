---
depends_on: [M001-8itnlq]
---

# M002-qqpa83: Pioneer Evaluation and Model Quality

**Gathered:** 2026-06-14
**Status:** Ready for planning

## Project Description

HuntAgent uses Pioneer/GLiNER2 for entity extraction from raw job-posting text. M002 builds an evaluation pipeline that compares Pioneer extraction against Gemini extraction on synthetic labeled data. It will conditionally fine-tune the Pioneer model if extraction gaps are found, targeting the Fastino side challenge. The evaluation results are stored as a structured event in PostgreSQL and displayed to the user via a Recharts-based visual comparison chart in the Next.js company dossier.

## Why This Milestone

To prove that Pioneer's extraction outperforms or replaces a general-purpose LLM API call. We need measured evidence to satisfy Fastino side challenge judges, showing thoughtful use of Pioneer features (synthetic data generation, evaluation against frontier models, and adaptive inference via fine-tuning).

## User-Visible Outcome

### When this milestone is complete, the user can:

- View a visual comparison chart (using Recharts) in the company dossier showing Pioneer vs Gemini extraction results.
- See evidence of fine-tuning if the base Pioneer model's performance dropped below the threshold.
- Trust extraction claims backed by concrete token-overlap F1 metrics.

### Entry point / environment

- Entry point: Backend evaluation scripts (`backend/eval/`), results surfaced via FastAPI and Next.js dossier UI.
- Environment: Local dev / CLI for eval runs, browser for dossier inspection.
- Live dependencies involved: Pioneer API, Gemini API, PostgreSQL.

## Completion Class

- Contract complete means: pytest suite passes using static JSON fixtures, confirming evaluation logic calculates F1 scores correctly.
- Integration complete means: evaluation results are correctly saved as `pioneer-eval` evidence events in PostgreSQL and rendered on the frontend.
- Operational complete means: Pioneer API downtime, Gemini API errors, or fine-tuning failures do not crash the pipeline; graceful degradation is enforced.

## Final Integrated Acceptance

To call this milestone complete, we must prove:

- 30-50 synthetic Tech & Startups job postings are generated via Gemini using Structured Outputs.
- Token overlap (F1 Score) metrics are computed comparing Pioneer against Gemini extraction.
- If the mean F1 score across all labels drops below 80%, a separate ~100 item training batch is generated and Pioneer fine-tuning is triggered.
- A visual Recharts comparison chart renders successfully in the Next.js company dossier based on the `pioneer-eval` evidence event.

## Architectural Decisions

### Evaluation pipeline as backend scripts

**Decision:** Build evaluation as backend scripts under `backend/eval/` rather than standalone notebooks or API endpoints.

**Rationale:** Scripts are testable with pytest, integrate with the existing backend structure, and can write outputs cleanly.

**Alternatives Considered:**
- API endpoints — adds unnecessary serving complexity for a batch evaluation task.
- Standalone notebooks — harder to test and integrate with the main codebase.

### Visual Comparison Charting Library

**Decision:** Use Recharts to render the visual comparison chart in the Next.js dossier UI.

**Rationale:** Recharts provides simple, declarative React components that look great out of the box and natively support radar/bar charts perfect for comparing multiple labels.

**Alternatives Considered:**
- Native HTML/CSS bars — too rudimentary for comparing multiple axes effectively.
- Chart.js — more complex setup with react-chartjs-2 compared to Recharts' declarative syntax.

### Fine-Tuning Failure Handling

**Decision:** Graceful degradation on fine-tuning failure. If the training API is inaccessible or fails, log the error and continue with the base model's evaluation results.

**Rationale:** Prevents a fragile external dependency (training API during a hackathon) from blocking the core evaluation pipeline and evidence display.

**Alternatives Considered:**
- Strict Blocking — rejected as it could break the pipeline completely if the API goes down.

## Error Handling Strategy

- Pioneer API unavailable → evaluation skips gracefully; existing circuit breaker pattern applies.
- Synthetic data generation fails → Gemini errors logged; evaluation runs only on successfully generated examples.
- Fine-tuning API errors/unavailability → Graceful degradation. Log error, skip fine-tuning, proceed with base model results.
- No secrets logged in results or evidence events.

## Risks and Unknowns

- Pioneer training API accessibility during hackathon — handled via graceful fallback.
- Synthetic data may lack real-world edge cases.
- Fine-tuning might not improve metrics above 80%.

## Existing Codebase / Prior Art

- `backend/tools/gliner_client.py` — Pioneer/GLiNER2 client.
- `backend/tools/gemini_client.py` — Gemini client.
- `docs/hackathon-resource-map.md` — Fastino side challenge context.

## Relevant Requirements

- R009 — Pioneer evaluation or fine-tuning.
- R002 — Resource attribution trail.
- R001 — Auditable company dossier.

## Scope

### In Scope

- Synthetic data generation (Tech/Startups) via Gemini Structured Outputs.
- F1 score evaluation script comparing Pioneer vs Gemini.
- Conditional fine-tuning logic (< 80% mean F1) with separate train batch generation.
- Saving metrics locally and injecting summary as `pioneer-eval` in Postgres.
- Next.js UI component for the visual comparison chart using Recharts.
- Pytest suite using static JSON fixtures.

### Out of Scope / Non-Goals

- Schema expansion beyond current 7 labels.
- Manual data curation.
- Adaptive inference optimizations (beyond conditional fine-tuning).

## Technical Constraints

- Scripts use `uv run`.
- Tests use `uv run pytest`.
- No secrets in logs.

## Integration Points

- Pioneer API (inference/training).
- Gemini API (synthetic data).
- PostgreSQL (evidence persistence).

## Testing Requirements

- Unit tests for F1 score calculation.
- Unit tests for conditional fine-tuning trigger logic.
- Integration tests using static JSON fixtures for mocked API responses.

## Acceptance Criteria

- 30-50 synthetic items generated and stored locally.
- Pioneer vs Gemini F1 metrics computed per label.
- Fine-tuning triggered (and separate train data generated) if mean F1 < 80% with graceful degradation if it fails.
- Visual comparison chart displays successfully in the Next.js dossier UI.
- Pytest suite passes.