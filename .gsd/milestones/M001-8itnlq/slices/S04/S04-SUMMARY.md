---
id: S04
parent: M001-8itnlq
milestone: M001-8itnlq
provides:
  - Dashboard-to-Telegram approval loop closure
  - Circuit-broken fal.ai visual evidence generation
  - UI controls for company approval/rejection in dossier
requires:
  - slice: S03
    provides: Dashboard company dossier UI surface and client-side types/components for evidence/resource display.
affects:
  []
key_files: []
key_decisions: []
patterns_established:
  - (none)
observability_surfaces:
  - none
drill_down_paths:
  []
duration: ""
verification_result: passed
completed_at: 2026-06-14T22:32:54.248Z
blocker_discovered: false
---

# S04: Approval and Optional Visual Layer

**Integrated dashboard approval synchronization with Telegram and added non-blocking fal.ai visual artifact generation.**

## What Happened

Slice S04 successfully integrated the human-in-the-loop approval loop between the Dashboard and Telegram, while safely adding the fal.ai visual artifact layer.

The backend now supports PATCH endpoints for company approval and rejection in `backend/api/dossier.py`. These endpoints update the database state and trigger a confirmation receipt via `backend/tools/telegram_client.py`. The orchestrator triggers downstream pipeline steps asynchronously upon dashboard approval.

The fal.ai integration is implemented in `backend/tools/fal_client.py` with a circuit-breaker pattern. Generation is spawned as a background task in `backend/agents/orchestrator.py` to ensure core pipeline transitions are non-blocking.

The frontend dossier page (`frontend/app/companies/[id]/page.tsx`) now integrates `ApprovalActions.tsx` for state mutations and `OptionalVisualDossier.tsx` for artifact rendering. The UI degrades gracefully when visual evidence is missing.

### Operational Readiness
- **Health Signal:** `EvidenceEvent` records with `resource_name='Telegram'` and `artifact_type='approval_state'`. Agent logs showing `Triggering async pipeline run`.
- **Failure Signal:** `fal` evidence events with `status='error'` or logs showing `Circuit breaker active`.
- **Recovery:** Missing fal artifacts are non-blocking. Approval sync failures are retryable from the UI.
- **Monitoring Gaps:** No proactive alerting for fal API quotas.

## Verification

Backend: 14 tests passed in `test_dossier.py`, `test_fal.py`, and `test_fal_client.py` using `uv run python -m pytest`.
Frontend: `npm run build` passed, confirming component integration and type safety.
Evidence: `gsd_exec` [0582f6e6-e3fe-4061-b5a2-1b2f88f9411e] (backend) and [05390ee6-0cd4-48c6-b2d6-5552fc43d7b1] (frontend).

## Requirements Advanced

None.

## Requirements Validated

- R001 — Verified via backend tests (test_fal_client.py) that the pipeline continues and records error evidence when the fal service or credentials fail. Core research flow is non-blocking.

## New Requirements Surfaced

None.

## Requirements Invalidated or Re-scoped

None.

## Operational Readiness

None.

## Deviations

None.

## Known Limitations

None.

## Follow-ups

None.

## Files Created/Modified

None.
