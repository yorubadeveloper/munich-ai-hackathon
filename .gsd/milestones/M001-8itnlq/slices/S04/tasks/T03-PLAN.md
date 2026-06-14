---
estimated_steps: 21
estimated_files: 4
skills_used: []
---

# T03: Add frontend approval actions and optional visual dossier component

Why: Users need to approve/reject from the dashboard and see fal visual artifacts when available.

Do:
1. In `frontend/lib/api.ts`, add two functions:
   - `approveCompany(companyId: string)` — PATCH to `/api/companies/${companyId}/approve`
   - `rejectCompany(companyId: string)` — PATCH to `/api/companies/${companyId}/reject`
   Both should return `{ status: string }` and swallow errors gracefully.
2. Create `frontend/components/ApprovalActions.tsx` — a client component ('use client') with Approve and Reject buttons:
   - Shows buttons only when `approval_state.status === 'pending'`.
   - On click, calls the API function, then uses `router.refresh()` to reload the page data.
   - Shows loading state during the API call.
   - After approval/rejection, buttons are replaced with a confirmation message.
3. Create `frontend/components/OptionalVisualDossier.tsx` — a client component that:
   - Accepts `events: EvidenceEvent[]` prop.
   - Finds the fal visual_artifact event from the evidence events array.
   - If a successful fal event exists with `payload.image_url`, renders the image in a styled card with the prompt text.
   - If a fal event exists with status='error', shows a muted placeholder: 'Visual artifact unavailable' with the error reason if present.
   - If no fal event exists at all, renders nothing (returns null).
4. In `frontend/app/companies/[id]/page.tsx`:
   - Import and render `<ApprovalActions>` in the Approval State section, passing the approval_state and company id.
   - Import and render `<OptionalVisualDossier>` above or below the Resource Analysis section, passing evidence_events.

Done when: Approval buttons appear on the dossier page for pending companies, the visual component renders or gracefully falls back, and `npm run build` succeeds in frontend/.

## Inputs

- `frontend/lib/api.ts`
- `frontend/app/companies/[id]/page.tsx`
- `frontend/components/ResourceChart.tsx`
- `frontend/components/StatusBadge.tsx`

## Expected Output

- `frontend/lib/api.ts`
- `frontend/components/ApprovalActions.tsx`
- `frontend/components/OptionalVisualDossier.tsx`
- `frontend/app/companies/[id]/page.tsx`

## Verification

cd frontend && npx next build
