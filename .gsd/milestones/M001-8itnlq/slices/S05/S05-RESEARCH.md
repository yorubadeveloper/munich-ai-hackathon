# Research: Verification and Demo Readiness (S05)

Verification of the Auditable Resource Dossier milestone (M001-8itnlq) focuses on proving the end-to-end evidence trail, ensuring UI robustness under partial failures, and providing a deterministic "Golden Path" for the hackathon demo.

## Summary
The system now supports structured `EvidenceEvent` persistence and a typed `CompanyDossierResponse`. S05 will close the quality loop by adding robust backend assertions, validating frontend type-safety, and creating a specialized seed script that showcases all hackathon resources (Tavily, Pioneer, Gemini, Telegram, fal) in a single reviewable dossier.

## Implementation Landscape

### Existing Patterns
- **Backend Tests:** Uses `pytest` and `pytest-mock` with async fixtures. `EvidenceEvent` fixtures are defined in `backend/tests/fixtures/evidence.py`.
- **API Contract:** Defined in `backend/api/dossier.py` using Pydantic models from `backend/schemas/dossier.py` and `backend/schemas/evidence.py`.
- **Frontend:** Next.js 16 (App Router) with `Recharts` for resource visualization. Components like `OptionalVisualDossier.tsx` and `ApprovalActions.tsx` are already integrated into the company detail page.
- **Circuit Breaking:** `fal_client.py` uses a fire-and-forget pattern with explicit error event recording.

### Dependencies
- **Backend:** `sqlalchemy` (Async), `pytest-mock`, `httpx` (for API testing).
- **Frontend:** `typescript`, `eslint`.
- **External:** Tavily, Gemini, Pioneer (GLiNER2), fal, Telegram (all to be mocked in tests).

### Constraints
- **Idempotency:** The seed script must be reusable without creating duplicate "Golden Path" records.
- **Non-blocking fal:** Verification must prove that missing fal artifacts do not crash the dossier or block approval.
- **Privacy:** Seed data must be realistic but fictional to avoid PII or credential leakage in logs.

## Recommendation
1. **Targeted Backend Testing:** Update `test_dossier.py` to specifically assert the presence of `fal` visual artifacts and the correct handling of `status='error'` events in the dossier response.
2. **"Golden Path" Seed Script:** Create `backend/scripts/seed_demo_dossier.py`. This script should use `SQLAlchemy` directly to insert a high-quality demo company ("Aetheria AI") with pre-populated evidence from all resources, including a simulated "fal" timeout to demonstrate failure visibility.
3. **Frontend Sanity:** Use `npm run typecheck` and `npm run lint` as the primary verification gates for UI stability.

## Tasks

### T01: Backend API Verification
- Update `backend/tests/test_dossier.py` to include assertions for `fal` visual evidence.
- Add a test case for "Dossier with Partial Failures" where one or more resources have an `error` status.
- Verify that PATCH `/approval` correctly triggers the Telegram receipt mock.
- **Verify:** `uv run pytest backend/tests/test_dossier.py`.

### T02: Golden Path Seed Script
- Create `backend/scripts/seed_demo_dossier.py`.
- Implement a `seed_demo()` function that creates a company with:
    - Tavily sources (URLs/snippets).
    - Pioneer entities (Tech stack, Funding).
    - Gemini reasoning (High fit score, detailed rationale).
    - fal visual artifact (mock URL).
    - A secondary "Failure Case" company to show the "Resource Unavailable" UI state.
- **Verify:** `uv run python backend/scripts/seed_demo_dossier.py` followed by checking the dashboard.

### T03: Frontend Quality Gate
- Run `npm run typecheck` in the `frontend/` directory to ensure dossier components match the new schemas.
- Run `npm run lint` to enforce code quality.
- Manual verification of the `OptionalVisualDossier` and `ResourceChart` components with the seeded data.
- **Verify:** Build output and lint results.

### T04: Milestone Validation
- Final integration check: Approve a company in the dashboard and verify the Telegram mock receives the notification.
- Verify the "Audit Trail" (EvidenceEvents) remains visible after approval.

## Risks and Mitigation
- **Database Schema Drift:** The seed script might fail if models changed but migrations weren't run. *Mitigation:* Script will check for table existence and use standard SQLAlchemy models.
- **Mock Fragility:** Tests might pass with mocks but fail in production. *Mitigation:* Use real Pydantic schemas for mock payloads to ensure structural parity.

## Infrastructure Impact
- **Observability:** Seeded data will populate the `ActivityFeed` and `ResourceChart`, providing a rich visual baseline for demoing observability.
- **CI/CD:** These checks form the basis for the "Ready for Hackathon" submission gate.
