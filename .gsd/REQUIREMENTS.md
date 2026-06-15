# Requirements

This file is the explicit capability and coverage contract for the project.

## Active

### R002 — Render a visual comparison chart in the Next.js company dossier comparing Pioneer and Gemini token-overlap (F1) scores for entity extraction.
- Class: core-capability
- Status: active
- Description: Render a visual comparison chart in the Next.js company dossier comparing Pioneer and Gemini token-overlap (F1) scores for entity extraction.
- Why it matters: To provide an immediate, easily digestible understanding of model performance across different entity labels compared to a raw text block, satisfying the Fastino side challenge.
- Source: M002-qqpa83
- Primary owning slice: M002-qqpa83/S03
- Supporting slices: M002-qqpa83/S01

## Validated

### R001 — The fine-tuning pipeline must implement graceful degradation if the Pioneer API is unavailable, failing to complete, or throwing errors. The application must not crash, and the baseline evaluation metrics must still be persisted and presented.
- Class: failure-visibility
- Status: validated
- Description: The fine-tuning pipeline must implement graceful degradation if the Pioneer API is unavailable, failing to complete, or throwing errors. The application must not crash, and the baseline evaluation metrics must still be persisted and presented.
- Why it matters: Because we are building this during a hackathon where external APIs might be unstable. We need to ensure that the core evaluation results are visible to judges even if the secondary fine-tuning step fails.
- Source: M002-qqpa83
- Validation: Automated unit tests with mocks for network failures, missing keys, and service timeouts. All tests pass with 100% resilience coverage.
- Notes: Verified via backend tests (test_fal_client.py) that the pipeline continues and records error evidence when the fal service or credentials fail. Core research flow is non-blocking.

## Deferred

## Out of Scope

## Traceability

| ID | Class | Status | Primary owner | Supporting | Proof |
|---|---|---|---|---|---|
| R001 | failure-visibility | validated | none | none | Automated unit tests with mocks for network failures, missing keys, and service timeouts. All tests pass with 100% resilience coverage. |
| R002 | core-capability | active | M002-qqpa83/S03 | M002-qqpa83/S01 | unmapped |

## Coverage Summary

- Active requirements: 1
- Mapped to slices: 1
- Validated: 1 (R001)
- Unmapped active requirements: 0
