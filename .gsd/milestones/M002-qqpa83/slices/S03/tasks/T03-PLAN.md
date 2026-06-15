---
estimated_steps: 6
estimated_files: 1
skills_used: []
---

# T03: Integrated Chart into Company Dossier

Run full verification suite:

1. `cd backend && uv run pytest` — all tests pass (existing + new eval tests).
2. `cd frontend && npm run typecheck` — no type errors.
3. `cd frontend && npm run lint` — no lint errors.
4. Review evidence event payload structure: confirm no secrets, correct schema.
5. Verify PioneerEvalChart handles edge cases: no pioneer-eval events, empty payload, missing labels.

## Inputs

- None specified.

## Expected Output

- Update the implementation and proof artifacts needed for this task.

## Verification

cd backend && uv run pytest && cd ../frontend && npm run typecheck && npm run lint
