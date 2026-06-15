---
id: T03
parent: S04
milestone: M001-8itnlq
key_files:
  - frontend/lib/api.ts
  - frontend/components/ApprovalActions.tsx
  - frontend/components/OptionalVisualDossier.tsx
  - frontend/app/companies/[id]/page.tsx
  - frontend/components/ResourceChart.tsx
  - frontend/components/ResourceChartInner.tsx
  - frontend/components/StatusBadge.tsx
key_decisions:
  - Approval actions only set local confirmation state and refresh the route on an explicit `{ status: 'success' }` response, leaving failed responses retryable without corrupting the UI state.
  - The optional fal visual artifact component returns null when no fal evidence exists so the core dossier review flow remains uncluttered and non-blocking.
duration: 
verification_result: passed
completed_at: 2026-06-14T22:21:41.062Z
blocker_discovered: false
---

# T03: Added frontend approval/rejection controls and optional fal visual artifact rendering to the company dossier page.

**Added frontend approval/rejection controls and optional fal visual artifact rendering to the company dossier page.**

## What Happened

Implemented the dashboard-facing portion of the S04 approval and optional visual layer. `frontend/lib/api.ts` now exposes `approveCompany` and `rejectCompany` helpers that PATCH the backend approval endpoints and return `{ status: string }`, falling back to `{ status: 'error' }` on client-side failures. `frontend/components/ApprovalActions.tsx` is a client component that renders Approve/Reject buttons only for pending approval state, disables controls while a request is in flight, records the submitted local status, and refreshes the Next.js route after a successful action. `frontend/components/OptionalVisualDossier.tsx` is a client component that finds fal `visual_artifact` evidence, renders the successful image and prompt when `payload.image_url` is available, returns null when no fal event exists, and renders a muted unavailable card with the error reason for failed or incomplete fal events. `frontend/app/companies/[id]/page.tsx` imports and renders the approval actions inside the Approval State section and the optional visual dossier alongside the evidence/resource analysis flow.

## Failure Modes
- Approval/rejection API unavailable, timeout, connection loss, or fetch exception: `approveCompany` and `rejectCompany` catch exceptions and return `{ status: 'error' }`, so the client component does not crash and leaves the user on the current dossier state.
- Approval/rejection endpoint returns a non-success status shape: `ApprovalActions` only swaps to the submitted confirmation and calls `router.refresh()` when `res.status === 'success'`; otherwise the pending controls remain available for retry.
- fal evidence missing: `OptionalVisualDossier` returns null so core company review remains unaffected.
- fal evidence reports error or lacks an image URL: `OptionalVisualDossier` renders the muted "Visual artifact unavailable" fallback and includes the backend error reason when present.
- Remote image loading failure after a successful URL is supplied is left to browser image behavior; the component still does not block dossier rendering.

## Load Profile
The first 10x-load pressure point for this task is repeated user-triggered PATCH requests from the dossier page, not client rendering. The component protects against same-session double-submit by disabling both buttons while a request is in flight, while backend approval state and Telegram synchronization remain the authoritative load/rate-limit boundary from T01. Visual dossier rendering adds only one optional image element for an already-persisted evidence event and performs no polling, fan-out, or additional backend calls.

## Negative Tests
No separate frontend test harness was added for this task. Negative-path behavior is covered by implementation-level guards verified by production compilation: API helpers catch fetch errors and return `{ status: 'error' }`; `ApprovalActions` ignores non-success responses instead of forcing a local approved/rejected state; `OptionalVisualDossier` handles absent events, error events, missing image URLs, and missing error context without throwing. Existing backend negative/contract tests for approval endpoints were delivered in T01.

## Verification

`npm --prefix frontend run build` completed successfully, proving the new API types, client components, dynamic chart wrapper, and dossier page imports/render sites compile in the Next.js production build. A focused static integration check confirmed the company dossier page contains the `ApprovalActions` and `OptionalVisualDossier` imports/render sites and passes `approval_state`/`evidence_events` data.

## Verification Evidence

| # | Command | Exit Code | Verdict | Duration |
|---|---------|-----------|---------|----------|
| 1 | `npm --prefix frontend run build` | 0 | ✅ pass | 14671ms |
| 2 | `python static check for ApprovalActions, OptionalVisualDossier, approval_state, evidence_events render sites in frontend/app/companies/[id]/page.tsx` | 0 | ✅ pass | 79ms |

## Deviations

Used `npm --prefix frontend run build` instead of changing directories before `npx next build` to honor the working-directory constraint. No frontend test harness was introduced because this repository slice uses the production Next.js build as the available frontend verification surface.

## Known Issues

No automated browser/UAT run was performed in this task because no running backend/frontend fixture with pending dossier data was available in the execution context.

## Files Created/Modified

- `frontend/lib/api.ts`
- `frontend/components/ApprovalActions.tsx`
- `frontend/components/OptionalVisualDossier.tsx`
- `frontend/app/companies/[id]/page.tsx`
- `frontend/components/ResourceChart.tsx`
- `frontend/components/ResourceChartInner.tsx`
- `frontend/components/StatusBadge.tsx`
