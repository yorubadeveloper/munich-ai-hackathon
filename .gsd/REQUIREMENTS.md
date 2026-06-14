# Requirements

This file is the explicit capability and coverage contract for the project.

## Active

### R001 — The fine-tuning pipeline must implement graceful degradation if the Pioneer API is unavailable, failing to complete, or throwing errors. The application must not crash, and the baseline evaluation metrics must still be persisted and presented.
- Class: failure-visibility
- Status: active
- Description: The fine-tuning pipeline must implement graceful degradation if the Pioneer API is unavailable, failing to complete, or throwing errors. The application must not crash, and the baseline evaluation metrics must still be persisted and presented.
- Why it matters: Because we are building this during a hackathon where external APIs might be unstable. We need to ensure that the core evaluation results are visible to judges even if the secondary fine-tuning step fails.
- Source: M002-qqpa83

### R002 — Render a visual comparison chart in the Next.js company dossier comparing Pioneer and Gemini token-overlap (F1) scores for entity extraction.
- Class: core-capability
- Status: active
- Description: Render a visual comparison chart in the Next.js company dossier comparing Pioneer and Gemini token-overlap (F1) scores for entity extraction.
- Why it matters: To provide an immediate, easily digestible understanding of model performance across different entity labels compared to a raw text block, satisfying the Fastino side challenge.
- Source: M002-qqpa83

## Validated

## Deferred

## Out of Scope

## Traceability

| ID | Class | Status | Primary owner | Supporting | Proof |
|---|---|---|---|---|---|
| R001 | failure-visibility | active | none | none | unmapped |
| R002 | core-capability | active | none | none | unmapped |

## Coverage Summary

- Active requirements: 2
- Mapped to slices: 0
- Validated: 0
- Unmapped active requirements: 2
