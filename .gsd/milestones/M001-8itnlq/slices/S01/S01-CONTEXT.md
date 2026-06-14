---
id: S01
milestone: M001-8itnlq
status: ready
---

# S01: Evidence Trail Backbone — Context

<!-- Slice-scoped context. Milestone-only sections (acceptance criteria, completion class,
     milestone sequence) do not belong here — those live in the milestone context. -->

## Goal

<!-- One sentence: what this slice delivers when it is done. -->

Establish the backend data structures and persistence mechanisms for structured resource and evidence events per company.

## Why this Slice

<!-- Why this slice is being done now. What does it unblock, and why does order matter? -->

This establishes the foundational data model required to make the pipeline auditable. It unblocks the API contract (S02) and UI display (S03) by ensuring we can actually store and query the evidence produced by external resources (Tavily, Gemini, etc.).

## Scope

<!-- What is and is not in scope for this slice. Be explicit about non-goals. -->

### In Scope

- Creating a dedicated database table for evidence events linked to a company, utilizing a JSON column for event-specific payloads.
- Implementing an append-only, immutable logging pattern for evidence events to preserve the timeline of actions.
- Defining the SQLAlchemy models and Pydantic schemas for evidence events.
- Creating standard `pytest` fixtures for the various evidence types (Tavily source, Pioneer extraction, Gemini reasoning, Telegram approval, fal visualization) to support testing here and in future slices.
- Handling pipeline failures by recording a failure event and explicitly halting further processing for that company to prevent low-confidence outreach generation.

### Out of Scope

- Implementing the FastAPI endpoints to serve this data to the frontend (handled in S02).
- Any frontend UI changes (handled in S03 and S04).
- Modifying the existing agent execution logic to *produce* these events in the live system (this slice only builds the capacity to store them and the examples).
- Handling actual fal integration logic.

## Constraints

<!-- Known constraints: time-boxes, hard dependencies, prior decisions this slice must respect. -->

- Must use PostgreSQL and SQLAlchemy.
- Evidence payloads must remain flexible (JSON) to accommodate different resource outputs without requiring schema migrations for every new AI tool.
- Must not remove existing company fields used by the current pipeline; the new evidence table is additive.

## Integration Points

<!-- Artifacts or subsystems this slice consumes and produces. -->

### Consumes

- `backend/database/models.py` (or similar) — Integrates with the existing `Company` model for foreign key relationships.

### Produces

- `backend/database/models.py` (or similar) — Adds the new `EvidenceEvent` model.
- `backend/schemas/evidence.py` (or similar) — Adds Pydantic schemas for validation and API documentation.
- `backend/tests/fixtures/evidence.py` (or similar) — Provides reusable `pytest` fixtures representing different event types.

## Open Questions

<!-- Unresolved questions at planning time. Answer them before or during execution. -->

- What is the exact taxonomy of `resource_name` and `artifact_type` strings to ensure consistency across the application? — We will define a strict Enum in Python for these to prevent typos and ensure type safety in the database.