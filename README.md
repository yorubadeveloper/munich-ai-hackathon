# HuntAgent

Stop sending applications into the void.
HuntAgent finds the companies, researches them, drafts your intro,
and asks you on Telegram before anything goes out.

Five agents run a ReAct loop — Think, Act, Observe, repeat — over shared
Postgres state. A human approves every outreach before it is sent.

## Stack
- **Backend:** FastAPI + PostgreSQL + SQLAlchemy async (Python 3.13, managed with uv)
- **Frontend:** Next.js 14 (App Router) · Quicksand font
- **Agents:** Gemini 2.0 Flash · Tavily · GLiNER2 (Pioneer)
- **Delivery:** Unipile (LinkedIn DM) · Resend (email)
- **Human loop:** Telegram Bot

## Quick Start (Docker)
```bash
cp .env.example .env
# DATABASE_URL is prefilled for Docker; add integration keys for full agent runs.
docker compose up --build
```

Open http://localhost:3000 -> set your profile -> hit Run Hunt.

## Local Backend Dev (uv)
The backend uses [uv](https://docs.astral.sh/uv/) for Python dependency
management — not pip. Dependencies live in `backend/pyproject.toml` and are
pinned in `backend/uv.lock`.

```bash
cd backend
uv sync                 # create .venv and install locked deps
uv run uvicorn main:app --reload --port 8000
```

Add or update a dependency:
```bash
uv add <package>        # updates pyproject.toml + uv.lock
uv lock                 # re-resolve after manual edits
```

To seed your profile via API instead of the UI:
```bash
curl -X POST http://localhost:8000/api/profile \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Your Name",
    "role": "Backend Engineer",
    "stack": ["Python", "FastAPI", "Postgres"],
    "location": "Munich / remote EU",
    "dealbreakers": ["unpaid", "internship"],
    "bio": "I build reliable backend systems...",
    "linkedin_url": "https://linkedin.com/in/you",
    "email": "you@example.com"
  }'
```

Then trigger a run and watch the log:
```bash
curl -X POST http://localhost:8000/api/run
curl http://localhost:8000/api/log
```

## Agent Loop
THINK -> ACT -> OBSERVE -> repeat until human gate.

```
Discovery -> Research -> [fit score >= 7?] -> Outreach draft
-> Telegram approval -> Delivery -> Follow-up watch
```

Agents never call each other directly. They read and write shared state in
Postgres. The orchestrator decides the next step from each company's `status`.

## Project Layout
```
huntagent/
├── backend/          FastAPI service
│   ├── agents/       discovery, research, outreach, delivery, followup, orchestrator
│   ├── tools/        tavily, gemini, gliner, unipile, telegram clients
│   ├── tg/           telegram bot (callback handlers)
│   └── api/          REST routes
└── frontend/         Next.js dashboard
```

> Note: the Telegram bot lives in `backend/tg/` (not `backend/telegram/`) so it
> does not shadow the installed `python-telegram-bot` package.

## Partners
- Google Gemini 2.5 Flash
- Resend (email)
- Tavily
- Pioneer / GLiNER2
- Aikido (connect repo for security scanning)
