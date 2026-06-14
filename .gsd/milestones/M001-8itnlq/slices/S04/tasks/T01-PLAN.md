---
estimated_steps: 10
estimated_files: 4
skills_used: []
---

# T01: Added dashboard approval and rejection PATCH endpoints with Telegram receipts and test cases.

Why: The dashboard can display the dossier but has no way to approve or reject a company. The Telegram bot should be notified when actions are taken from the dashboard to keep the human operator informed.

Do:
1. In `backend/api/dossier.py`, add two PATCH endpoints:
   - `PATCH /api/companies/{company_id}/approve` — sets company.status to 'approved', creates a Telegram EvidenceEvent (approval_state, approved=True, source='dashboard'), sends a receipt message to Telegram via `telegram_client._send_message`, and returns updated company status.
   - `PATCH /api/companies/{company_id}/reject` — sets company.status to 'rejected', creates a Telegram EvidenceEvent (approval_state, approved=False, source='dashboard'), sends a receipt message to Telegram, and returns updated company status.
2. Both endpoints must handle the case where company is not found (404) and where telegram credentials are missing (log warning, don't crash).
3. In `backend/tools/telegram_client.py`, add a `send_dashboard_receipt(company_name: str, action: str)` function that sends a simple text message like '✅ {company_name} approved via Dashboard' or '❌ {company_name} rejected via Dashboard' to the configured chat_id. Use the existing `_send_message` helper.
4. In `backend/schemas/dossier.py`, add a simple `ApprovalActionResponse` schema with `status: str` and `company_id: UUID`.
5. Register the new routes in main.py if not already included.

Done when: Both PATCH endpoints exist, the Telegram receipt helper is added, and `uv run ruff check .` passes.

## Inputs

- `backend/api/dossier.py`
- `backend/tools/telegram_client.py`
- `backend/schemas/dossier.py`
- `backend/models.py`
- `backend/config.py`
- `backend/tg/bot.py`

## Expected Output

- `backend/api/dossier.py`
- `backend/tools/telegram_client.py`
- `backend/schemas/dossier.py`

## Verification

cd backend && uv run ruff check backend/api/dossier.py backend/tools/telegram_client.py backend/schemas/dossier.py
