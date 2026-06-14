---
id: S03
milestone: M001-8itnlq
status: ready
---

# S03: Dashboard Company Dossier — Context

<!-- Slice-scoped context. Milestone-only sections (acceptance criteria, completion class,
     milestone sequence) do not belong here — those live in the milestone context. -->

## Goal

<!-- One sentence: what this slice delivers when it is done. -->

Build a side-drawer UI component in the Next.js dashboard that consumes the dossier API to display categorized evidence, outreach drafts, and inline failure states, allowing users to approve or reject outreach directly.

## Why this Slice

<!-- Why this slice is being done now. What does it unblock, and why does order matter? -->

This is the primary user-visible deliverable of the milestone. It transforms the abstract backend evidence (from S01/S02) into the actual trust-building UI where the human-in-the-loop can inspect why a company was recommended and make an informed approval decision. It unblocks S04 by providing the surface where the optional fal visual layer will eventually live.

## Scope

<!-- What is and is not in scope for this slice. Be explicit about non-goals. -->

### In Scope

- Creating a Next.js Side Drawer (slide-over) component triggered from the existing company cards/pipeline view.
- Fetching data from the new `GET /companies/{id}/dossier` endpoint.
- Rendering evidence in **Categorized Sections** (e.g., "Web Research (Tavily)", "Extracted Entities (Pioneer)", "Reasoning (Gemini)").
- Displaying the drafted outreach hook.
- Showing partial resource failures inline within their respective categories using clear visual indicators (e.g., red badges or alert boxes).
- Adding 'Approve' and 'Reject' action buttons directly inside the dossier drawer, wired to the appropriate backend state updates.

### Out of Scope

- Integrating the optional fal visual layer (handled in S04).
- Removing or disabling the Telegram bot approval flow; the dashboard buttons are additive, not a replacement.
- Modifying the underlying backend pipeline logic.

## Constraints

<!-- Known constraints: time-boxes, hard dependencies, prior decisions this slice must respect. -->

- Must use existing Next.js / React patterns and Tailwind/UI libraries already present in `frontend/`.
- The dossier must handle missing data gracefully (e.g., if Pioneer extraction hasn't happened yet, it shouldn't crash the drawer).

## Integration Points

<!-- Artifacts or subsystems this slice consumes and produces. -->

### Consumes

- `GET /companies/{id}/dossier` — The typed API contract created in S02.
- `frontend/components/PipelineBoard.tsx` (or similar) — To add the trigger/click handler to open the dossier.

### Produces

- `frontend/components/CompanyDossierDrawer.tsx` (or similar) — The new drawer component.
- `frontend/types/dossier.ts` (or similar) — Client-side TypeScript interfaces matching the S02 contract.

## Open Questions

<!-- Unresolved questions at planning time. Answer them before or during execution. -->

- How does the dashboard stay in sync if a user approves via Telegram while looking at the drawer? — Current thinking: Rely on standard SWR/React Query polling or revalidation on focus, rather than building WebSockets just for this edge case.