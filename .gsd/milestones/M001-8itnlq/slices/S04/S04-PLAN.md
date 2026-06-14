# S04: Approval and Optional Visual Layer

**Goal:** Integrate the Telegram approval synchronization logic and safely embed the optional fal visual artifact generation into the background research phase without blocking the core dossier review flow.
**Demo:** The review flow preserves Telegram approval and can show optional fal-style visual output without blocking core company review.

## Must-Haves

- Dashboard approve/reject endpoints exist and update company status + create Telegram evidence events
- Approving or rejecting via dashboard sends a receipt message to the Telegram chat
- fal client is circuit-broken: missing credentials or API errors produce a graceful EvidenceEvent with status=error
- fal generation runs as a fire-and-forget background step during the research phase, never blocking the pipeline
- Frontend renders the fal visual artifact when available, or a clean placeholder when unavailable
- Existing dossier tests pass; new tests cover approval endpoints and fal client failure modes
- `uv run ruff check .` passes in backend

## Proof Level

- This slice proves: integration

## Integration Closure

Upstream: S03 dossier UI (frontend/app/companies/[id]/page.tsx), S02 dossier API (backend/api/dossier.py, backend/schemas/dossier.py, backend/schemas/evidence.py). New wiring: approval PATCH endpoints in dossier.py, fal_client.py tool, fal trigger in orchestrator.py, OptionalVisualDossier component in frontend, approval action buttons in dossier page. What remains: S05 verification and demo readiness.

## Verification

- EvidenceEvent records for fal generation (success or failure) with resource_name=fal, artifact_type=visual_artifact. EvidenceEvent records for dashboard approval actions with resource_name=Telegram, artifact_type=approval_state. Agent logs from orchestrator for fal trigger and approval state changes.

## Tasks

- [x] **T01: Added dashboard approval and rejection PATCH endpoints with Telegram receipts and test cases.** `est:45m`
  Why: The dashboard can display the dossier but has no way to approve or reject a company. The Telegram bot should be notified when actions are taken from the dashboard to keep the human operator informed.
  - Files: `backend/api/dossier.py`, `backend/tools/telegram_client.py`, `backend/schemas/dossier.py`, `backend/main.py`
  - Verify: cd backend && uv run ruff check backend/api/dossier.py backend/tools/telegram_client.py backend/schemas/dossier.py

- [ ] **T02: Create circuit-broken fal client and wire into research pipeline** `est:45m`
  Why: The hackathon requires a creative fal.ai integration. It must be non-blocking — missing credentials or API failures must never crash the pipeline.
  - Files: `backend/tools/fal_client.py`, `backend/config.py`, `backend/pyproject.toml`, `backend/agents/orchestrator.py`
  - Verify: cd backend && uv run ruff check backend/tools/fal_client.py backend/config.py backend/agents/orchestrator.py

- [ ] **T03: Add frontend approval actions and optional visual dossier component** `est:50m`
  Why: Users need to approve/reject from the dashboard and see fal visual artifacts when available.
  - Files: `frontend/lib/api.ts`, `frontend/components/ApprovalActions.tsx`, `frontend/components/OptionalVisualDossier.tsx`, `frontend/app/companies/[id]/page.tsx`
  - Verify: cd frontend && npx next build

- [ ] **T04: Add tests for approval endpoints and fal client failure modes** `est:40m`
  Why: We need to verify the new approval endpoints work correctly and that the fal client degrades gracefully.
  - Files: `backend/tests/test_dossier.py`, `backend/tests/test_fal.py`
  - Verify: cd backend && uv run python -m pytest tests/test_fal.py -v --tb=short

## Files Likely Touched

- backend/api/dossier.py
- backend/tools/telegram_client.py
- backend/schemas/dossier.py
- backend/main.py
- backend/tools/fal_client.py
- backend/config.py
- backend/pyproject.toml
- backend/agents/orchestrator.py
- frontend/lib/api.ts
- frontend/components/ApprovalActions.tsx
- frontend/components/OptionalVisualDossier.tsx
- frontend/app/companies/[id]/page.tsx
- backend/tests/test_dossier.py
- backend/tests/test_fal.py
