# S01: Evidence Trail Backbone

**Goal:** Establish the backend data structures and persistence mechanisms for structured resource and evidence events per company.
**Demo:** A company can expose structured resource/evidence events for sources, entities, reasoning, and draft hooks through backend data structures or persistence.

## Must-Haves

- Complete the planned slice outcomes.

## Verification

- Run the task and slice verification checks for this slice.

## Tasks

- [x] **T01: Verified implementation of backend Evidence models and schemas.** `est:1h`
  Create EvidenceEvent models and schemas in the backend.
  - Files: `backend/models.py`, `backend/schemas/evidence.py`
  - Verify: pytest backend/tests/

## Files Likely Touched

- backend/models.py
- backend/schemas/evidence.py
