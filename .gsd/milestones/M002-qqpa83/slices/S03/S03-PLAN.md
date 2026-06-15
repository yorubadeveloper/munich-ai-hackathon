# S03: Evaluation Persistence and Visual Comparison Chart

**Goal:** Persist evaluation metrics as pioneer-eval evidence events via the existing EvidenceEvent model, and render a Recharts comparison chart in the frontend company dossier.
**Demo:** After this, evaluation results are saved as pioneer-eval evidence events in PostgreSQL. The Next.js company dossier renders a Recharts BarChart showing per-label F1 scores for Pioneer vs Gemini. npm run typecheck and npm run lint pass.

## Must-Haves

- 1. Evaluation results saved as EvidenceEvent with artifact_type='pioneer-eval' in PostgreSQL\n2. Dossier API returns pioneer-eval events with per-label F1 payload\n3. New PioneerEvalChart component renders a Recharts BarChart with per-label F1 scores\n4. Chart integrated into company dossier page next to existing ResourceChart\n5. npm run typecheck and npm run lint pass\n6. No secrets in evidence event payloads

## Proof Level

- This slice proves: pytest for DB persistence + npm typecheck/lint for frontend

## Integration Closure

End-to-end: eval script → DB → API → React chart renders correctly

## Verification

- Evidence events queryable via existing dossier API

## Tasks

- [x] **T01: Persisted Evaluation Results as EvidenceEvents** `est:20min`
  Create `backend/eval/persist.py` with a `persist_eval_results` function:
  - Files: `backend/eval/persist.py`, `backend/tests/test_eval_persist.py`
  - Verify: cd backend && uv run pytest tests/test_eval_persist.py -v

- [x] **T02: Built Recharts Visual Comparison Chart** `est:25min`
  Create `frontend/components/PioneerEvalChart.tsx`:
  - Files: `frontend/components/PioneerEvalChart.tsx`, `frontend/app/companies/[id]/page.tsx`
  - Verify: cd frontend && npm run typecheck && npm run lint

- [x] **T03: Integrated Chart into Company Dossier** `est:15min`
  Run full verification suite:
  - Verify: cd backend && uv run pytest && cd ../frontend && npm run typecheck && npm run lint

## Files Likely Touched

- backend/eval/persist.py
- backend/tests/test_eval_persist.py
- frontend/components/PioneerEvalChart.tsx
- frontend/app/companies/[id]/page.tsx
