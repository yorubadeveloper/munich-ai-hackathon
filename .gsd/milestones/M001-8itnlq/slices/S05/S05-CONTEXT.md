---
id: S05
milestone: M001-8itnlq
status: ready
---

# S05: Verification and Demo Readiness — Context

<!-- Slice-scoped context. Milestone-only sections (acceptance criteria, completion class,
     milestone sequence) do not belong here — those live in the milestone context. -->

## Goal

<!-- One sentence: what this slice delivers when it is done. -->

Prove the end-to-end evidence trail works through local backend tests, strict frontend checks, and a reliable database seed script for the hackathon demo.

## Why this Slice

<!-- Why this slice is being done now. What does it unblock, and why does order matter? -->

It guarantees the milestone is actually finished and presentable. By building a dedicated "Golden Path" seed script, we ensure the hackathon demo narrative is flawless and immune to live API rate limits or latency, while automated tests prove the underlying contract is sound.

## Scope

<!-- What is and is not in scope for this slice. Be explicit about non-goals. -->

### In Scope

- Writing backend `pytest` unit tests to verify the `EvidenceEvent` persistence (S01) and the Dossier API response shape (S02), including partial failure states.
- Stubbing the Python client wrappers (e.g., Tavily, Gemini tools) during backend tests to ensure fast, deterministic verification without live API calls.
- Verifying the Next.js frontend via strict type-checking (`npm run typecheck`) and linting (`npm run lint`), alongside manual review of the dossier drawer.
- Creating a dedicated database seed script (e.g., `backend/scripts/seed_demo_dossier.py`) that populates a "Golden Path" company with rich, realistic evidence events across all resource types (including the optional fal artifact and a partial failure example) specifically for the judge demo.

### Out of Scope

- Setting up heavy End-to-End browser tests (like Playwright/Cypress).
- Writing tests that make live HTTP calls to external APIs.
- Broad CI/CD pipeline configuration (we rely on existing local commands or basic GitHub Actions).

## Constraints

<!-- Known constraints: time-boxes, hard dependencies, prior decisions this slice must respect. -->

- Backend tests must run via `uv run pytest`.
- Seed script must be idempotent or easily resettable so it can be run reliably right before the demo.

## Integration Points

<!-- Artifacts or subsystems this slice consumes and produces. -->

### Consumes

- All code produced in S01-S04.
- `backend/tests/fixtures/evidence.py` (created in S01).

### Produces

- `backend/tests/api/test_dossier.py` (updated with full assertions).
- `backend/scripts/seed_demo_dossier.py` — The demo data generator.

## Open Questions

<!-- Unresolved questions at planning time. Answer them before or during execution. -->

- What specific company and scenario should the "Golden Path" seed script represent? — Current thinking: A highly relevant fictional or real AI tooling company that perfectly highlights why the Gemini reasoning score is high, alongside a clear, localized failure (e.g., fal timeout) to prove we don't hide errors.