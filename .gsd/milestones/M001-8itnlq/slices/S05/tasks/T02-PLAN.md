---
estimated_steps: 14
estimated_files: 1
skills_used: []
---

# T02: Verified the deterministic Golden Path demo seed script (Aetheria AI + Nebula Robotics with full evidence trail and a partial-failure fal event)

**Why:** The hackathon demo needs a deterministic, realistic company dossier that showcases every resource type (Tavily, Pioneer, Gemini, Telegram, fal) and a partial-failure state — independent of live API calls.

**Do:**
1. Create `backend/scripts/seed_demo_dossier.py` as an async Python script that:
   a. Imports `database.init_db`, `database.AsyncSessionLocal`, and `models` (Company, Research, EvidenceEvent, Message).
   b. Uses a well-known deterministic UUID (e.g., `uuid5` with namespace URL and name 'aetheria-ai') for the Golden Path company so the script is idempotent (merge-by-id).
   c. Creates a Company 'Aetheria AI' (status='approved', fit_score=0.92, website, job_url).
   d. Creates a Research record with realistic `funding_stage`, `tech_stack`, `fit_reasoning`, `hiring_manager`.
   e. Creates EvidenceEvents for: Tavily source (2 URLs), Pioneer entity_extraction, Gemini reasoning, Telegram approval_state (approved), fal visual_artifact (mock image URL).
   f. Creates a second company 'Nebula Robotics' (status='researched', fit_score=0.65) with a fal evidence event that has `status='error'`, `error_context={'code':'timeout','message':'fal API timed out after 30s'}` — demonstrating failure visibility.
   g. Creates a Message record for 'Aetheria AI' with a drafted outreach.
   h. Uses `merge()` or existence checks for idempotency.
2. The script must run standalone: `uv run python scripts/seed_demo_dossier.py` from `backend/`.
3. Print a summary of what was seeded on success.

**Done-when:** The seed script runs without error against an initialized DB, creates both companies with evidence, and re-running it does not duplicate records.

## Inputs

- `backend/models.py`
- `backend/database.py`
- `backend/config.py`
- `backend/schemas/evidence.py`

## Expected Output

- `backend/scripts/seed_demo_dossier.py`

## Verification

test -f backend/scripts/seed_demo_dossier.py && cd backend && uv run python -c "import scripts.seed_demo_dossier; print('module imports OK')"
