# S03: Dashboard Dossier Visual Card UI

**Goal:** Update the Next.js dashboard to display the fal visual card in the dossier, with graceful degradation if generation fails or is missing.
**Demo:** Dashboard shows the generated visual card in the company dossier, or gracefully degrades when unavailable.

## Must-Haves

- The dossier UI shows the visual card if present
- The UI gracefully degrades if the card is missing or failed to generate

## Proof Level

- This slice proves: browser

## Integration Closure

S03 provides the user-facing capability, completing the fal feature loop.

## Verification

- None natively required on the frontend; failures quietly degrade visually.

## Tasks

- [x] **T01: Visual Component implemented into Next.js UI** `est:30m`
  Update frontend data fetching (`frontend/lib/api.ts`) or corresponding frontend components to pull the fal evidence URL from the company dossier object.
  - Files: `frontend/lib/api.ts`
  - Verify: Run typescript compiler.

- [x] **T02: Mounted OptionalVisualDossier UI in Page** `est:1h`
  Create or update a React component (`frontend/components/OptionalVisualDossier.tsx` or similar) to render the image. Include fallback states for when the image is pending or unavailable.
  - Files: `frontend/components/OptionalVisualDossier.tsx`, `frontend/app/companies/[id]/page.tsx`
  - Verify: Run `npm run lint` and `npm run typecheck` in frontend.

## Files Likely Touched

- frontend/lib/api.ts
- frontend/components/OptionalVisualDossier.tsx
- frontend/app/companies/[id]/page.tsx
