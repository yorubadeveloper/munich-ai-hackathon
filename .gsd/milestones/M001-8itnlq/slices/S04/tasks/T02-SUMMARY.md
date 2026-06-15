---
id: T02
parent: S04
milestone: M001-8itnlq
key_files:
  - backend/tools/fal_client.py
  - backend/config.py
  - backend/pyproject.toml
  - backend/agents/orchestrator.py
  - backend/tests/test_fal_client.py
key_decisions:
  - Spawned the fal visual generation in a background asyncio.create_task to ensure API rate limits or slow image generation never block downstream transitions to researched or draft_ready status.
duration: 
verification_result: passed
completed_at: 2026-06-14T21:35:53.605Z
blocker_discovered: false
---

# T02: Implemented circuit-broken fal.ai client and integrated async visual artifact generation into company research

**Implemented circuit-broken fal.ai client and integrated async visual artifact generation into company research**

## What Happened

Added fal_key setting to the configuration class and added fal-client to pyproject.toml dependencies. Created a circuit-broken fal_client module under tools/ using the modern fal-client Python SDK with subscribe_async and a 30-second timeout. Integrated _trigger_fal_generation into the orchestrator agent loop as a fire-and-forget background task triggered after research completes. The background task writes a successful or error-prone EvidenceEvent record to PostgreSQL without blocking the main workflow pipeline. Comprehensive unit tests covering authentication, network exceptions, database writes, and background orchestration were implemented in test_fal_client.py, and all 36 tests passed successfully.

## Verification

Executed uv run ruff check on modified files, which returned success. Ran pytest unit tests in the backend workspace using PYTHONPATH=. uv run pytest resulting in all 36 test cases passing, including mocks verifying behavior under active key, empty key, network exception, and database write success/failure states.

## Verification Evidence

| # | Command | Exit Code | Verdict | Duration |
|---|---------|-----------|---------|----------|
| 1 | `uv run ruff check tools/fal_client.py config.py agents/orchestrator.py` | 0 | ✅ pass | 60ms |
| 2 | `PYTHONPATH=. uv run pytest` | 0 | ✅ pass | 1686ms |

## Deviations

None.

## Known Issues

None.

## Files Created/Modified

- `backend/tools/fal_client.py`
- `backend/config.py`
- `backend/pyproject.toml`
- `backend/agents/orchestrator.py`
- `backend/tests/test_fal_client.py`
