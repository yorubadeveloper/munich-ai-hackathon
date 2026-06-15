---
id: T02
parent: S05
milestone: M001-8itnlq
key_files:
  - (none)
key_decisions:
  - (none)
duration: 
verification_result: mixed
completed_at: 2026-06-14T23:47:09.444Z
blocker_discovered: false
---

# T02: Verified the deterministic Golden Path demo seed script (Aetheria AI + Nebula Robotics with full evidence trail and a partial-failure fal event)

**Verified the deterministic Golden Path demo seed script (Aetheria AI + Nebula Robotics with full evidence trail and a partial-failure fal event)**

## What Happened

The seed script `backend/scripts/seed_demo_dossier.py` was already present and fully implemented to the T02 contract. I validated it against the live `models.py` (Company, Research, Message, EvidenceEvent) and the task plan, confirming every required surface:

- Deterministic IDs via `uuid.uuid5(NAMESPACE_URL, ...)` with merge-by-id (`session.get` existence checks) for idempotency.
- Company "Aetheria AI" (status=approved, fit_score=0.92, website, job_url) plus a Research record (funding_stage, headcount_estimate, tech_stack, fit_reasoning, hiring_manager_* fields — note the model uses `hiring_manager_name/role/linkedin/email`, not a single `hiring_manager` field).
- EvidenceEvents covering every resource type: Tavily source (2 URLs), Pioneer entity_extraction, Gemini reasoning, Telegram approval_state=approved, and fal visual_artifact (mock image URL).
- Second company "Nebula Robotics" (status=researched, fit_score=0.65) with a fal EvidenceEvent carrying status='error' and error_context {code: timeout, message: ...} to demonstrate failure visibility.
- A drafted Message for Aetheria AI.
- Standalone runnable via sys.path injection so `uv run python scripts/seed_demo_dossier.py` works from `backend/`, with a printed summary on success.

The authoritative verification command (module import) passes. The fuller "re-run does not duplicate" check requires a live PostgreSQL instance; none is running in this environment (asyncpg connection refused on localhost:5432), so the runtime path could not be exercised here. The idempotency logic is structurally sound (get-then-update / add) and the script was reviewed line-by-line against the schema.

No code changes were needed — the deliverable already satisfied the contract.

### Failure Modes (Q5)
External dependency: PostgreSQL via `database.AsyncSessionLocal` / `init_db` (asyncpg). On connection loss or timeout the script raises the asyncpg error and exits non-zero (observed live: `ConnectionRefusedError` propagates cleanly with a full traceback), so failures are loud rather than silent. Malformed/missing schema would surface as SQLAlchemy errors on first query. No other external APIs are called (the resource events are mock/static), so there is no network or subprocess fan-out to handle.

### Load Profile (Q6)
Not applicable — this is a one-shot, single-transaction demo seed run with a fixed two-company dataset and no runtime load dimension.

### Negative Tests (Q7)
Not applicable — this is a demo seed utility, not a tested surface. Idempotency (the only meaningful negative case) is enforced structurally via deterministic uuid5 IDs and get-before-insert, and is exercised by re-running the script against a live DB during the demo.

## Verification

Ran the authoritative plan verification command: `test -f backend/scripts/seed_demo_dossier.py && cd backend && uv run python -c "import scripts.seed_demo_dossier; print('module imports OK')"` → exit 0, "module imports OK". Cross-checked all field names against backend/models.py. Full DB seed run could not complete because no PostgreSQL server is running (asyncpg connection refused, localhost:5432) — environment limitation, not a script defect.

## Verification Evidence

| # | Command | Exit Code | Verdict | Duration |
|---|---------|-----------|---------|----------|
| 1 | `test -f backend/scripts/seed_demo_dossier.py && cd backend && uv run python -c "import scripts.seed_demo_dossier; print('module imports OK')"` | 0 | ✅ pass | 1500ms |
| 2 | `cd backend && timeout 8 uv run python scripts/seed_demo_dossier.py` | 1 | ⚠️ blocked (no Postgres in env; connection refused) | 8000ms |

## Deviations

None.

## Known Issues

None.

## Files Created/Modified

None.
