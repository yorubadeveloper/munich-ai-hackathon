# Research: S04 - Approval and Optional Visual Layer

## Summary
Slice S04 finalizes the human-in-the-loop experience by synchronizing Dashboard and Telegram approvals and introduces a creative visual layer using `fal.ai`. The system already has the plumbing for company research and outreach drafting, but the "Approval" step is currently heavily tied to the Telegram bot. This slice exposes approval via the Dashboard API and adds an optional, non-blocking visual dossier artifact.

## Recommendation
1.  **Add Approval API:** Implement a `PATCH /companies/{id}/approve` and `PATCH /companies/{id}/reject` endpoint in `backend/api/dossier.py`. This should reuse the logic from `backend/tg/bot.py:_approve_and_send` to ensure consistency.
2.  **Dashboard-Telegram Sync:** When approved via Dashboard, use the `telegram_client` to send a "Dashboard Approved" message to the Telegram chat to keep the human operator informed.
3.  **Circuit-Broken fal Client:** Create `backend/tools/fal_client.py` using `fal-client`. It must handle missing API keys and timeouts gracefully.
4.  **Async fal Generation:** Trigger `fal` generation as a background task during the `research` or `outreach` agent phase. Store the result (image URL) as an `EvidenceEvent` with `resource_name="fal"` and `artifact_type="visual_dossier"`.
5.  **Graceful Frontend Fallback:** Create `frontend/components/OptionalVisualDossier.tsx` to render the `fal` image. If no image exists or it failed, show a simple placeholder or skip the section entirely to avoid breaking the UI.

## Implementation Landscape

### Backend Changes
- **`backend/api/dossier.py`**: Add approval/rejection endpoints.
- **`backend/tools/fal_client.py`**: New tool for interacting with `fal.ai`.
- **`backend/agents/research.py` or `orchestrator.py`**: Inject the `fal` generation call.
- **`backend/config.py`**: Add `fal_key` to `Settings`.

### Frontend Changes
- **`frontend/app/companies/[id]/page.tsx`**: Add "Approve" and "Reject" buttons.
- **`frontend/components/OptionalVisualDossier.tsx`**: New component for the visual artifact.
- **`frontend/lib/api.ts`**: Add `approveCompany` and `rejectCompany` functions.

### Data Model
- **`EvidenceEvent`**: Will be used to store `fal` results.
- **`Company.status`**: Will transition from `pending_approval` to `approved` or `rejected`.

## Don't Hand-Roll
- Use `fal-client` for AI generation.
- Use `telegram_client` for bot notifications.
- Use `EvidenceEvent` for tracking artifacts.

## Verification Plan

### Automated Tests
- `backend/tests/test_dossier.py`: Test the new approval/rejection endpoints.
- `backend/tests/test_fal.py`: Test the `fal` client with mocked API responses and failure modes (missing key).

### Manual Verification
- Approve a company via the Dashboard and verify the Telegram bot receives a notification and the company moves to the `sent` pipeline phase.
- Trigger research for a new company and verify an `EvidenceEvent` for `fal` is created (even if it's a failure event if keys are missing).
- Inspect the dossier UI to ensure the visual section renders or fails gracefully.
