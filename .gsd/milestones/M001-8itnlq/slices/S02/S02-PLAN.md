# S02: Dossier API Contract

**Goal:** Create a unified dossier API response that includes company details, research, messages, and evidence trail.
**Demo:** The dashboard can request a typed company dossier containing evidence, resource labels, fit reasoning, outreach hook, approval state, and partial-failure data.

## Must-Haves

- Complete the planned slice outcomes.

## Verification

- Run the task and slice verification checks for this slice.

## Tasks

- [x] **T01: Verified implementation of the Dossier API contract.** `est:1h`
  Implement the /dossier API endpoint and corresponding response schemas.
  - Files: `backend/api/dossier.py`, `backend/schemas/dossier.py`
  - Verify: pytest backend/tests/

## Files Likely Touched

- backend/api/dossier.py
- backend/schemas/dossier.py
