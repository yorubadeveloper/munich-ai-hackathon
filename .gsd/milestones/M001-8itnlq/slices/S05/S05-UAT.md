# S05: Verification and Demo Readiness — UAT

**Milestone:** M001-8itnlq
**Written:** 2026-06-15T00:03:28.461Z

## UAT: Verification and Demo Readiness

**UAT Type:** artifact-driven (static/file checks and command-line test execution only — no runtime server or browser verification, since this slice adds no new runtime surfaces).

### Preconditions
- Repo checked out at `/home/jovyan/munich-ai-hackathon`.
- Backend deps installed (`uv sync --group dev` in `backend/`).
- Frontend deps installed (`npm install` in `frontend/`).

### Check 1 — Dossier API tests cover fal visual + partial failure
1. `cd backend && PYTHONPATH=. uv run pytest tests/test_dossier.py -v`
- **Expected:** Exit 0; all dossier tests pass, including assertions for fal visual evidence presence and error-only/partial-failure handling. (Observed: 7 passed.)

### Check 2 — Full backend suite, no regressions
1. `cd backend && PYTHONPATH=. uv run pytest -q`
- **Expected:** Exit 0; all tests pass (observed: 40 passed, 3 subtests). No regressions across evidence, fal, Tavily, and safe-http tests.

### Check 3 — Seed script integrity
1. `test -f backend/scripts/seed_demo_dossier.py`
2. `cd backend && PYTHONPATH=. uv run python -c "import scripts.seed_demo_dossier; print('module imports OK')"`
- **Expected:** File exists; module imports cleanly (exit 0, "module imports OK").
- **Edge case (DB-backed environment):** Running the seed against an initialized PostgreSQL produces a Golden Path company with evidence across all 6 resource types plus a partial-failure fal event and a failure-case company.

### Check 4 — Frontend static analysis
1. `cd frontend && npm run typecheck`
2. `cd frontend && npm run lint`
- **Expected:** Both exit 0; dossier component sources compile and lint clean against the project's TypeScript config.

### Edge Cases
- **No database available:** Seed script import still succeeds; full seed run is deferred to a DB-backed environment (documented limitation).
- **Error-only dossier:** Dossier API response includes partial-failure evidence honestly rather than omitting it (asserted in Check 1).
