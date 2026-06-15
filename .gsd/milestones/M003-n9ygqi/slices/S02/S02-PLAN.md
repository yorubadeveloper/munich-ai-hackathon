# S02: Backend Pipeline fal Integration

**Goal:** Integrate the fal generation automatically after the research phase completes, ensuring it runs once per company and stores the generated URL as an evidence event.
**Demo:** Running the pipeline generates and saves a fal visual card evidence event to the database.

## Must-Haves

- Pipeline calls fal client post-research
- Only one card is generated per company (URL is reused)
- The URL is saved as an evidence event (resource: `fal`)

## Proof Level

- This slice proves: integration

## Integration Closure

S02 provides the saved fal evidence in the DB that S03 will render in the frontend.

## Verification

- Pipeline logs track the fal generation step and evidence persistence.

## Tasks

- [x] **T01: Integrated fal into Research Pipeline** `est:1h`
  Update the orchestrator logic (`backend/agents/orchestrator.py`) to trigger the fal client generation after research completes. Ensure it handles failure gracefully (non-blocking).
  - Files: `backend/agents/orchestrator.py`
  - Verify: Check linter and pipeline test logic.

- [x] **T02: Mapped visual outputs to EvidenceEvents** `est:1h`
  Implement logic to save the resulting fal image URL as an evidence event in the database, verifying first that one hasn't already been created to prevent duplicate generation.
  - Files: `backend/agents/orchestrator.py`, `backend/models.py`
  - Verify: Run integration test showing evidence creation.

## Files Likely Touched

- backend/agents/orchestrator.py
- backend/models.py
