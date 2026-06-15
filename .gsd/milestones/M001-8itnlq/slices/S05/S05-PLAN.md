# S05: Verification and Demo Readiness

**Goal:** Prove the end-to-end evidence trail works through extended backend tests (covering fal visual artifacts and partial-failure assertions), strict frontend checks (typecheck + lint), and a deterministic Golden Path seed script for the hackathon demo.
**Demo:** Local tests/checks prove the evidence flow, UI wiring, partial-failure behavior, and hackathon resource demo narrative.

## Must-Haves

- `uv run pytest backend/tests/test_dossier.py` passes with assertions covering all 6 resource types including fal visual evidence and error-state events.
- `npm run typecheck` in `frontend/` exits 0.
- `npm run lint` in `frontend/` exits 0.
- `backend/scripts/seed_demo_dossier.py` runs without error against an initialized DB and produces a Golden Path company with evidence events for all resource types plus a failure-case company.
- All existing backend tests still pass (`uv run pytest`).

## Proof Level

- This slice proves: unit-tests + static-analysis

## Integration Closure

S05 consumes all code from S01–S04. It produces no new runtime code — only tests, type checks, and a seed script. The dossier test exercises the S02 API contract end-to-end (mocked DB). The frontend checks validate that S03/S04 components type-check against the S02 schema types. The seed script validates the S01 EvidenceEvent model can be populated for all resource types.

## Verification

- None — verification-only slice; no new runtime surfaces.

## Tasks

- [x] **T01: Extended dossier API tests with Fal visual and partial-failure assertions, validating both the presence of visual evidence and robust handling of error-only evidence.** `est:25 min`
  **Why:** The existing `test_dossier.py` includes `partial_failure_evidence` and several resource types but omits the `fal_evidence` fixture. The test does not explicitly assert that fal visual artifacts appear in the dossier response or that dossiers containing only error events are handled correctly. This task closes the test gap.
  - Files: `backend/tests/test_dossier.py`
  - Verify: cd backend && uv run pytest tests/test_dossier.py -v

- [x] **T02: Verified the deterministic Golden Path demo seed script (Aetheria AI + Nebula Robotics with full evidence trail and a partial-failure fal event)** `est:35 min`
  **Why:** The hackathon demo needs a deterministic, realistic company dossier that showcases every resource type (Tavily, Pioneer, Gemini, Telegram, fal) and a partial-failure state — independent of live API calls.
  - Files: `backend/scripts/seed_demo_dossier.py`
  - Verify: test -f backend/scripts/seed_demo_dossier.py && cd backend && uv run python -c "import scripts.seed_demo_dossier; print('module imports OK')"

- [x] **T03: Verified frontend typecheck and lint both pass clean (exit 0) for the dossier components — no fixes required.** `est:15 min`
  **Why:** The dossier components (OptionalVisualDossier, ApprovalActions, ResourceChart, ResourceChartInner) were added in S03/S04. This task proves they compile cleanly against the TypeScript project and pass linting.
  - Files: `frontend/components/OptionalVisualDossier.tsx`, `frontend/components/ApprovalActions.tsx`, `frontend/components/ResourceChart.tsx`, `frontend/components/ResourceChartInner.tsx`
  - Verify: cd frontend && npm run typecheck && npm run lint

- [x] **T04: Confirmed full backend pytest suite passes clean (40 passed, 3 subtests, exit 0) with no regressions after S05 test additions.** `est:10 min`
  **Why:** After T01's test additions, we must confirm no regressions across all backend tests — including the fal, evidence, and Tavily client tests established in S01–S04.
  - Verify: cd backend && uv run pytest -v

## Files Likely Touched

- backend/tests/test_dossier.py
- backend/scripts/seed_demo_dossier.py
- frontend/components/OptionalVisualDossier.tsx
- frontend/components/ApprovalActions.tsx
- frontend/components/ResourceChart.tsx
- frontend/components/ResourceChartInner.tsx
