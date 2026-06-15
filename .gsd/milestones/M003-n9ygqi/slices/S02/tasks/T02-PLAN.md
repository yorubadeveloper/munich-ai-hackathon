---
estimated_steps: 1
estimated_files: 2
skills_used: []
---

# T02: Mapped visual outputs to EvidenceEvents

Implement logic to save the resulting fal image URL as an evidence event in the database, verifying first that one hasn't already been created to prevent duplicate generation.

## Inputs

- `backend/models.py`

## Expected Output

- `backend/agents/orchestrator.py`

## Verification

Run integration test showing evidence creation.

## Observability Impact

Evidence event persistence is logged.
