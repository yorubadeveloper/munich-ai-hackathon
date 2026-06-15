---
id: S03
milestone: M002-qqpa83
status: ready
---

# S03: Evaluation Persistence and Visual Comparison Chart — Context

<!-- Slice-scoped context. Milestone-only sections (acceptance criteria, completion class,
     milestone sequence) do not belong here — those live in the milestone context. -->

## Goal

Persist Pioneer evaluation results as `pioneer-eval` evidence and render a clear Recharts comparison chart in the company dossier that helps users and judges trust the model-quality story.

## Why this Slice

S01 produces local Pioneer-vs-Gemini metrics and S02 adds conditional fine-tuning lifecycle status; S03 turns those local artifacts into durable product evidence by saving them to PostgreSQL and displaying them in the dossier where the user already reviews company evidence.

## Scope

### In Scope

- Persist S01/S02 evaluation outputs as `pioneer-eval` evidence events in PostgreSQL.
- Attach the evaluation event to a selected or configured demo company record so the chart appears in the existing company dossier flow.
- Make clear in the UI copy that this is model-quality evidence attached for demo/review purposes, not company-specific research about that company.
- Store latest-run summary data suitable for the dossier: per-label F1, macro mean F1, sample counts, lifecycle status, fine-tuning trigger decision, training status/job id when present, degraded reason when present, generated timestamp, and local artifact paths.
- Persist a few small curated mismatch examples for the weakest labels so the dossier can explain low scores without storing full raw outputs.
- Render a Recharts comparison chart that primarily communicates trust evidence: whether Pioneer is credible compared with Gemini, where each label is strong or weak, and what the macro mean says overall.
- Use a simple interactive chart with readable labels and hover tooltips rather than complex drilldowns.
- Include a short plain-English takeaway near the chart, such as which labels Pioneer handled best and where it struggled.
- Show transparent but non-blocking degraded states: render the chart when base metrics exist, while displaying calm badges/reasons for pending, unavailable, partial, or failed fine-tuning states.
- Show a quiet empty evidence prompt when no `pioneer-eval` event exists, explaining that Pioneer evaluation has not been run yet.
- Use calm evidence language in statuses and empty states rather than celebratory or overly diagnostic copy.
- Prove S03 with deterministic fixture data: persistence of a `pioneer-eval` event, dossier rendering of the chart from that event, and frontend lint/typecheck passing.

### Out of Scope

- Running live Gemini or Pioneer evaluation; S01/S02 own generation, scoring, and training submission.
- Blocking UI rendering on fine-tuning completion.
- Adding a new global model-quality dashboard or navigation surface outside the company dossier.
- Persisting full raw per-item extraction outputs, raw API logs, authorization headers, or sensitive request metadata.
- Implementing deep chart drilldowns or extensive per-item debugging UI.
- Expanding beyond the current seven labels: `company_name`, `job_title`, `tech_stack`, `company_stage`, `hiring_manager`, `salary`, and `remote_policy`.
- Proving that fine-tuning improved post-training metrics; S02 only records submission/fallback status and S03 surfaces that status.

## Constraints

- S03 depends on S01 local metric artifacts and S02 lifecycle artifacts; it should not duplicate metric calculation or training-trigger logic.
- The `pioneer-eval` evidence payload must be safe to persist and display: no secrets, raw tokens, sensitive headers, or unnecessary raw API dumps.
- Degraded or pending states must remain visible rather than silently hiding the evaluation chart when base metrics exist.
- The UI should keep the dossier trustworthy and readable for judges: plain language, clear counts, and no over-claiming model performance.
- Fixture-based verification is preferred so S03 can be tested without live API dependencies or credit usage.
- Existing decisions apply: use Recharts for visualization and preserve graceful degradation for training failures.
- The implementation should preserve the existing company dossier evidence-review experience rather than creating a separate model-evaluation product surface.

## Integration Points

### Consumes

- `backend/eval/` S01 metric artifacts — Provides per-label F1, macro mean F1, sample counts, mismatch examples, and local artifact paths.
- `backend/eval/` S02 lifecycle artifacts — Provides fine-tuning trigger decision, training status, job id when returned, degraded reason, and preserved base metrics.
- `backend/models.py` / evidence event model — Provides the PostgreSQL persistence shape for `pioneer-eval` evidence events.
- Existing FastAPI evidence/dossier data path — Supplies persisted evidence events to the frontend dossier.
- `frontend/components/ResourceChartInner.tsx` or the existing dossier chart area — Existing Recharts-based UI surface to extend for `pioneer-eval` data.
- Deterministic fixture payloads — Used to prove persistence and rendering without live API calls.

### Produces

- `pioneer-eval` evidence event payload — Durable PostgreSQL event containing summary metrics, lifecycle status, fine-tuning status, curated examples, artifact links, and timestamps.
- Dossier chart rendering branch/component — Recharts UI that displays per-label Pioneer-vs-Gemini F1 evidence with hover details and readable labels.
- Empty/degraded state UI copy — Calm placeholders and badges for not-run, pending, unavailable, partial, or failed fine-tuning/evaluation states.
- Persistence and UI verification fixtures — Static data proving the event can be saved and rendered.
- Frontend verification evidence — Passing `npm run typecheck` and `npm run lint` for the S03 UI changes.

## Open Questions

- Exact company/demo record selection mechanism for attaching the global evaluation event — current thinking: accept or configure a target demo company explicitly rather than silently choosing an arbitrary company.
- Exact `pioneer-eval` payload schema field names — current thinking: keep them stable, explicit, and close to S01/S02 artifact names so S03 does not reinterpret prior outputs.
- Exact wording for the no-event placeholder and degraded badges — current thinking: use calm evidence language such as “Pioneer evaluation not available yet,” “Base metrics available; fine-tuning pending,” and “Showing base Pioneer metrics because training was unavailable.”
