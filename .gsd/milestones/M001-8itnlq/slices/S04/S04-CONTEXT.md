---
id: S04
milestone: M001-8itnlq
status: ready
---

# S04: Approval and Optional Visual Layer — Context

<!-- Slice-scoped context. Milestone-only sections (acceptance criteria, completion class,
     milestone sequence) do not belong here — those live in the milestone context. -->

## Goal

<!-- One sentence: what this slice delivers when it is done. -->

Integrate the Telegram approval synchronization logic and safely embed the optional fal visual artifact generation into the background research phase without blocking the core dossier review flow.

## Why this Slice

<!-- Why this slice is being done now. What does it unblock, and why does order matter? -->

It finalizes the human-in-the-loop experience by ensuring actions taken in the new Dashboard Dossier (S03) stay synchronized with the existing Telegram bot flow. It also introduces the creative hackathon requirement (fal) in a safe, non-destructive way that doesn't break the critical path if credentials are missing or the service is unstable.

## Scope

<!-- What is and is not in scope for this slice. Be explicit about non-goals. -->

### In Scope

- Wiring the dashboard approval/rejection actions (from S03) to trigger a confirmation receipt message back to the Telegram bot, closing the loop.
- Integrating a lightweight, asynchronous fal generation step into the backend's existing background research pipeline.
- Creating a safe fallback mechanism where missing fal credentials or generation failures result in a clean placeholder card/badge in the UI, rather than a broken page or raw error.
- Ensuring the `fal` evidence event conforms to the S01/S02 API contract.

### Out of Scope

- Building complex custom fal workflows or LoRA training; we are using a standard, stable fal template/endpoint for a simple visual artifact (e.g., a synthesized company logo or concept card).
- Making the Telegram bot the *only* place approval can happen (dashboard approval is now fully supported and synced).

## Constraints

<!-- Known constraints: time-boxes, hard dependencies, prior decisions this slice must respect. -->

- **Crucial:** fal integration MUST be non-blocking. If it fails, the rest of the company research and the dossier review must still succeed.
- Must use existing background task patterns (e.g., APScheduler or whatever is currently running the agents) for the fal generation.

## Integration Points

<!-- Artifacts or subsystems this slice consumes and produces. -->

### Consumes

- `backend/tg/bot.py` / `backend/tools/telegram_client.py` — To send the "Approved/Rejected via Dashboard" receipt.
- `backend/api/routes/dossier.py` — To handle the approval mutation.
- `frontend/components/CompanyDossierDrawer.tsx` — S03's UI, to inject the new fal placeholder/image component.

### Produces

- `backend/tools/fal_client.py` (or similar) — A new, circuit-broken client for the optional fal integration.
- `frontend/components/OptionalVisualDossier.tsx` (or similar) — The UI component that handles rendering the fal artifact or its fallback placeholder gracefully.

## Open Questions

<!-- Unresolved questions at planning time. Answer them before or during execution. -->

- What exact visual is fal generating that adds value? — Current thinking: A synthesized "opportunity card" or abstract visualization of the company's core product, based on the Tavily/Pioneer summary. We will keep it simple and prompt-driven to ensure stability.