---
estimated_steps: 6
estimated_files: 4
skills_used: []
---

# T03: Frontend Type-Check and Lint Verification

**Why:** The dossier components (OptionalVisualDossier, ApprovalActions, ResourceChart, ResourceChartInner) were added in S03/S04. This task proves they compile cleanly against the TypeScript project and pass linting.

**Do:**
1. Run `npm run typecheck` in `frontend/` — fix any type errors found in dossier-related components.
2. Run `npm run lint` in `frontend/` — fix any lint violations in dossier-related files.
3. If fixes are needed, make minimal targeted edits only to the affected component files.

**Done-when:** Both `npm run typecheck` and `npm run lint` exit 0 in `frontend/`.

## Inputs

- `frontend/tsconfig.json`
- `frontend/package.json`

## Expected Output

- `frontend/components/OptionalVisualDossier.tsx`
- `frontend/components/ApprovalActions.tsx`
- `frontend/components/ResourceChart.tsx`
- `frontend/components/ResourceChartInner.tsx`

## Verification

cd frontend && npm run typecheck && npm run lint
