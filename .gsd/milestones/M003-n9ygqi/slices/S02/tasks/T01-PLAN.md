---
estimated_steps: 1
estimated_files: 1
skills_used: []
---

# T01: Integrate fal call into orchestrator

Update the orchestrator logic (`backend/agents/orchestrator.py`) to trigger the fal client generation after research completes. Ensure it handles failure gracefully (non-blocking).

## Inputs

- `backend/tools/fal_client.py`

## Expected Output

- `backend/agents/orchestrator.py`

## Verification

Check linter and pipeline test logic.

## Observability Impact

Pipeline logs when fal generation is initiated.
