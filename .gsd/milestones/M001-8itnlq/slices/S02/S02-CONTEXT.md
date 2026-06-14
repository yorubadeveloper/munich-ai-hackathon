---
id: S02
milestone: M001-8itnlq
status: ready
---

# S02: Dossier API Contract — Context

<!-- Slice-scoped context. Milestone-only sections (acceptance criteria, completion class,
     milestone sequence) do not belong here — those live in the milestone context. -->

## Goal

<!-- One sentence: what this slice delivers when it is done. -->

Create a typed FastAPI endpoint that aggregates a company and its structured evidence events into a single, unpaginated dossier response, cleanly exposing partial failures and approval state.

## Why this Slice

<!-- Why this slice is being done now. What does it unblock, and why does order matter? -->

It bridges the gap between the raw backend persistence created in S01 and the frontend UI needs of S03. By defining a strict, typed API contract first, we ensure the dashboard has a reliable shape to render, including how to handle missing data and errors, before building the UI components.

## Scope

<!-- What is and is not in scope for this slice. Be explicit about non-goals. -->

### In Scope

- Creating a single `GET /companies/{id}/dossier` endpoint.
- Defining Pydantic models for the dossier response, ensuring it includes the base company data, an unpaginated array of evidence events, and a dedicated `approval_state` object.
- Representing partial failures within the evidence events array (e.g., an event with `status="error"` and an `error_detail` payload) rather than abstracting them away.
- Exposing raw event types to the frontend so it can derive resource labels (e.g., 'tavily_search', 'gemini_reasoning').
- Writing backend tests verifying the shape of the endpoint using the S01 fixtures.

### Out of Scope

- Implementing the frontend dashboard UI (S03).
- Adding pagination to the evidence events array (assuming a small number of events per company for this milestone).
- Modifying the underlying Telegram approval logic; this slice only reads and surfaces its current state.

## Constraints

<!-- Known constraints: time-boxes, hard dependencies, prior decisions this slice must respect. -->

- Must build upon the SQLAlchemy models and schemas established in S01.
- The API response must strictly type the various possible evidence payloads (using discriminated unions in Pydantic if necessary) to provide a solid contract for the TypeScript frontend.

## Integration Points

<!-- Artifacts or subsystems this slice consumes and produces. -->

### Consumes

- `backend/database/models.py` (or similar) — S01 EvidenceEvent and Company models.
- `backend/schemas/evidence.py` (or similar) — S01 base schemas.

### Produces

- `backend/api/routes/dossier.py` (or similar) — The new FastAPI router for the dossier.
- `backend/schemas/dossier.py` (or similar) — The Pydantic response models defining the contract.
- `backend/tests/api/test_dossier.py` (or similar) — Tests proving the endpoint returns the correct shape, including failure states.

## Open Questions

<!-- Unresolved questions at planning time. Answer them before or during execution. -->

- Do we need to support filtering or sorting the evidence events within the dossier endpoint? — Current thinking: No, return all events chronological by default to keep the API simple; the frontend can sort or filter if needed for display.