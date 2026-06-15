---
depends_on: [M001-8itnlq]
---

# M002-qqpa83: Pioneer Evaluation and Model Quality

**Gathered:** 2026-06-15
**Status:** Draft in discussion

## Project Description

HuntAgent will add a backend evaluation pipeline for the current 7-label Pioneer/GLiNER2 extraction contract. The pipeline generates 30-50 synthetic Tech & Startups job postings with explicit expected labels using Gemini Structured Outputs, compares Pioneer and Gemini extraction against those expected labels with token-overlap F1 metrics, persists a `pioneer-eval` evidence event in PostgreSQL, and renders a Recharts comparison chart in the Next.js company dossier.

## Discussion Decisions So Far

- Primary shape: judge-facing proof for the Fastino challenge.
- Evaluation truth source: synthetic labeled examples with expected labels, not Gemini-as-judge circular scoring.
- Result location: one project-level/latest `pioneer-eval` evidence event surfaced in the dossier UI.
- Fine-tuning policy: call real Pioneer training only when access/credentials are available and mean F1 is below threshold; otherwise record skipped/failed status gracefully.
- Label scope: stay inside the current 7-label extraction schema.
- Live proof boundary: completion requires a DB-backed chart rendered from a real PostgreSQL event; external AI APIs may be mocked in automated tests and best-effort in live runs.

## Open Questions

- Exact user-facing chart framing and fallback copy when evaluation or fine-tuning is unavailable.
- Whether synthetic dataset and train batch should be versioned locally as fixtures/artifacts after generation.
- What operational statuses must be persisted on the `pioneer-eval` event for demo clarity.
