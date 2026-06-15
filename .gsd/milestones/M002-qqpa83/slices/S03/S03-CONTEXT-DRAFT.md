---
id: S03
milestone: M002-qqpa83
status: draft
---

# S03: Evaluation Persistence and Visual Comparison Chart — Context Draft

## Goal

Persist Pioneer evaluation lifecycle results as `pioneer-eval` evidence and render a clean dossier chart that makes model-quality evidence understandable to users and judges.

## Confirmed Human Decisions So Far

- The chart should primarily communicate trust evidence: whether Pioneer is credible compared with Gemini, with per-label F1 bars, macro mean, and a short plain-English takeaway.
- Degraded or partial states should be transparent but non-blocking: render the chart when base metrics exist, and show a clear badge/reason for pending, unavailable, or degraded fine-tuning states.
- Persistence should optimize for a latest-run evidence event with summary metrics, lifecycle status, training status/job id, artifact paths, and generated timestamp.
- The chart should be a simple interactive Recharts view with hover tooltips and readable labels, avoiding complex drilldown as required scope.
- If no `pioneer-eval` event exists, the dossier should show a quiet empty evidence prompt explaining that evaluation has not been run yet.
- S03 done proof should use deterministic fixture data to prove persistence and chart rendering, with frontend lint/typecheck passing and no live API dependency.

## Open Questions

- How a global evaluation run should be associated with a specific company dossier or demo company record.
- Whether mismatch examples belong in the persisted event now or should remain local artifact links only.
- Exact wording and status vocabulary for chart badges and empty states.
