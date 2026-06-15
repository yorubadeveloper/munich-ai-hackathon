# HuntAgent — Architecture & Design

> Stop sending applications into the void. HuntAgent finds the companies,
> researches them, drafts your intro, and asks you on Telegram before anything
> goes out.

This document explains **what HuntAgent is**, **how it is built**, and **why the
pieces fit together the way they do**. It is written for engineers joining the
project or reviewers trying to understand the system end to end.

---

## 1. The Idea

In 2020 the author wrote a single cold email to a CTO and it took them from
Nigeria to Munich. No network, no referral, no recruiter — just research, one
honest message, and one shot. It worked, but doing it well took real effort, and
it only happened **once**.

HuntAgent automates that exact loop for every company you care about:

1. **Discover** companies worth your time.
2. **Research** each one (funding, tech stack, the right person to talk to).
3. **Draft** a personal intro that references a project you actually built.
4. **Approve** — you say yes on Telegram before anything is sent.
5. **Send** by LinkedIn DM or email, then watch for replies and draft follow-ups.

It is **not a chatbot** and **not a prompt wrapper**. It is a stateful
multi-agent pipeline with a human-in-the-loop approval gate.

---

## 2. System Overview

```
                         ┌──────────────────────────────┐
                         │          Frontend            │
                         │   Next.js 16 · React 19      │
                         │   /  ·  /dashboard  ·  /setup │
                         └───────────────┬──────────────┘
                                         │ REST (JSON, polled every 4s)
                                         ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                              Backend (FastAPI)                             │
│                                                                            │
│   API layer        ┌─────────┐ ┌─────────┐ ┌─────┐ ┌─────┐                 │
│   /api/...         │companies│ │ profile │ │ run │ │ log │                 │
│                    └─────────┘ └─────────┘ └──┬──┘ └─────┘                 │
│                                               │ triggers                   │
│   Orchestrator  ◄─────────────────────────────┘                           │
│   (ReAct loop)     reads/writes shared state, decides next step           │
│        │                                                                   │
│        ├─► Discovery ─► Research ─► Outreach ─► (gate) ─► Delivery         │
│        │                                                   ▲               │
│        └─► Follow-up (hourly background task) ─────────────┘               │
│                                                                            │
│   Tools     Tavily · Gemini · GLiNER2/Pioneer · Unipile · Resend · TG      │
└───────────────────────────────┬────────────────────────────────────────────┘
                                 │ async SQLAlchemy
                                 ▼
                        ┌─────────────────┐        ┌──────────────────┐
                        │   PostgreSQL    │        │  Telegram (human │
                        │  shared state   │◄──────►│   approval gate) │
                        └─────────────────┘        └──────────────────┘
```

**Core architectural principle:** agents never call each other directly. They
read and write shared state in Postgres, and the **orchestrator** decides what
happens next based on each company's `status`. This makes the pipeline
inspectable, resumable, and resilient — any step can fail and be retried without
corrupting the others.

---

## 3. Tech Stack

| Layer | Choice | Version |
|---|---|---|
| Frontend framework | Next.js (App Router) | 16.2.9 |
| UI runtime | React | 19.2 |
| Icons | @phosphor-icons/react | 2.1.10 |
| Animation | lottie-web | 5.13.0 |
| Font | Figtree (`next/font`) | — |
| Backend framework | FastAPI | 0.136.3 |
| ASGI core | Starlette | 1.3.1 |
| ASGI server | Uvicorn | 0.49.0 |
| ORM | SQLAlchemy (async) | 2.0.50 |
| DB driver | asyncpg | 0.31.0 |
| Database | PostgreSQL | 15 |
| LLM | Google Gemini (`gemini-3.5-flash`, configurable) | SDK 0.7.0 |
| Web search | Tavily | 0.3.3 |
| Entity extraction | GLiNER2 via Pioneer inference API | — |
| Outreach delivery | Unipile (LinkedIn DM) · Resend (email) | — |
| Human approval | python-telegram-bot | 21.3 |
| Background scheduling | apscheduler / asyncio loop | 3.10.4 |
| Python | CPython | 3.13 |
| Python packaging | uv (not pip) | — |

---

## 4. Repository Layout

```
huntagent/
├── backend/                      FastAPI service (Python 3.13, managed by uv)
│   ├── main.py                   App factory, lifespan, CORS, router wiring
│   ├── config.py                 Pydantic settings (all secrets via env)
│   ├── database.py               Async engine, session factory, init_db()
│   ├── models.py                 SQLAlchemy models (shared state schema)
│   ├── agents/
│   │   ├── orchestrator.py       ReAct loop; status-driven step selection
│   │   ├── discovery.py          Find companies (Tavily + GLiNER2)
│   │   ├── research.py           Enrich + fit score (Tavily + Gemini)
│   │   ├── outreach.py           Draft message (Gemini), pick relevant project
│   │   ├── delivery.py           Send via Unipile or Resend
│   │   └── followup.py           Hourly reply check + follow-up drafts
│   ├── tools/
│   │   ├── tavily_client.py      Web search (threaded, async-safe)
│   │   ├── gemini_client.py      LLM calls + robust JSON extraction
│   │   ├── gliner_client.py      Pioneer inference API (no local torch)
│   │   ├── unipile_client.py     LinkedIn DM + Resend email
│   │   └── telegram_client.py    Outbound approval/notify messages
│   ├── tg/
│   │   └── bot.py                Telegram callback handlers (resume loop)
│   ├── api/
│   │   ├── companies.py          GET /api/companies
│   │   ├── profile.py            GET/POST /api/profile
│   │   ├── run.py                POST /api/run
│   │   └── log.py                GET /api/log
│   ├── pyproject.toml            uv dependencies (canonical)
│   ├── uv.lock                   Fully pinned lockfile
│   └── Dockerfile                uv-based image (Python 3.13)
│
├── frontend/                     Next.js 16 dashboard
│   ├── app/
│   │   ├── layout.tsx            Figtree font, root layout
│   │   ├── globals.css           Warm monochrome ("stone") design system
│   │   ├── page.tsx              Landing page (the story + how it works)
│   │   ├── dashboard/page.tsx    Live pipeline + activity + Run Hunt
│   │   └── setup/page.tsx        Profile form (incl. projects/links)
│   ├── components/
│   │   ├── StatBar.tsx           Animated counters
│   │   ├── PipelineBoard.tsx     Companies grouped by status
│   │   ├── CompanyCard.tsx       Fit-score ring + tags
│   │   ├── StatusBadge.tsx       Per-status pill
│   │   ├── ActivityFeed.tsx      Live agent timeline
│   │   └── Lottie.tsx            Client-only Lottie loader
│   ├── lib/api.ts                Fetch helpers (no-store, UTC-safe)
│   ├── public/signal.json        Hero Lottie animation
│   └── Dockerfile                Node 22 image
│
├── docker-compose.yml            db + backend + frontend
├── .env / .env.example           Shared config for both services
├── README.md                     Quick start
└── ARCHITECTURE.md               This document
```

---

## 5. The Agents

Five agents, each a single responsibility. They communicate only through the
database.

### 5.1 Orchestrator (`agents/orchestrator.py`)
The brain. Implements the **ReAct loop** — Think → Act → Observe → repeat — for a
single company, driven entirely by its `status`:

```
discovered ──► research ──► (fit < 7?) ──► skipped_low_fit
                  │
                  ▼ researched
              outreach draft ──► draft_ready ──► [TELEGRAM GATE: loop pauses]
                                                        │ user taps "Send it"
                                                        ▼ approved
                                                   delivery ──► sent
```

- `run_discovery()` is the entry point (called by `POST /api/run`). It runs the
  Discovery agent, then spawns one independent `run_pipeline(company_id)` task
  per discovered company.
- Each loop iteration is wrapped in try/except with rollback + an error log, so
  one company's failure never takes down the others.
- The loop **pauses** at the human gate and is **resumed** by the Telegram
  callback handler — not by polling. This is what makes it a true
  human-in-the-loop system.

### 5.2 Discovery (`agents/discovery.py`)
- **Think:** the user wants `{role}` near `{location}` — where do I search?
- **Act:** Tavily searches across job boards and company pages.
- **Observe:** GLiNER2 (via Pioneer) extracts structured entities (company name,
  etc.), dealbreakers are filtered, results are deduplicated by URL, and new
  `Company` rows are written with `status="discovered"`.

### 5.3 Research (`agents/research.py`)
- **Act:** Tavily searches for funding, hiring manager, tech signals, recent news.
- **Observe:** Gemini synthesizes the raw results into a structured profile and
  produces a **fit score (1–10)**. A `Research` row is written and linked to the
  company. Score `< 7.0` → the company is skipped.

### 5.4 Outreach (`agents/outreach.py`)
- **Act:** Gemini drafts a message using the company research **and the user's
  bio + projects**. The prompt forces the model to reference exactly one specific
  company detail and exactly one relevant project the user has built.
- **Channel choice:** LinkedIn if a hiring-manager LinkedIn URL exists, else email.
- **Observe:** the draft is saved as a `Message` with `status="pending"` and
  handed to the Telegram gate.

### 5.5 Delivery (`agents/delivery.py`)
- Runs only after a message is `approved`.
- LinkedIn DM via **Unipile**, or email via **Resend** (derives a `jobs@domain`
  fallback if no hiring-manager email is known).
- Stores a `conversation_id` for later reply tracking and sets `status="sent"`.

### 5.6 Follow-up (`agents/followup.py`)
- A background task that runs **every hour** (`schedule_followup_checks`).
- For each `sent` message: checks Unipile for LinkedIn replies. If a reply is
  found → notify the user on Telegram. If 5+ days of silence → draft a follow-up
  and send it to the Telegram gate for approval.

---

## 6. The Human-in-the-Loop Gate

Nothing is sent without explicit approval. This is a first-class architectural
feature, not an afterthought.

```
Outreach drafts ──► tools/telegram_client.send_approval_request()
                         │  (message + ✅ Send it / ❌ Skip buttons)
                         ▼
                    Your phone (Telegram)
                         │  you tap a button
                         ▼
                    tg/bot.py  handle_callback()
                         │  approve:  set status=approved, resume pipeline
                         │  skip:     set status=skipped_by_user
                         ▼
                    Orchestrator resumes ──► Delivery sends
```

The bot also handles `followup_approve` / `followup_skip` for the follow-up flow.
The Telegram bot runs as an asyncio task started in the FastAPI lifespan and
polls for callback queries.

> Note: the bot module lives in `backend/tg/` (not `backend/telegram/`) so it
> does not shadow the installed `python-telegram-bot` package, whose import name
> is `telegram`.

---

## 7. Data Model (shared state)

All state lives in Postgres. The status fields on `Company` and `Message` are the
"program counter" the orchestrator reads.

| Table | Purpose | Key fields |
|---|---|---|
| `user_profile` | The single user. Drives discovery + outreach. | `role`, `stack[]`, `location`, `dealbreakers[]`, `bio`, `projects`, `github_url`, `portfolio_url`, `linkedin_url`, `email` |
| `companies` | Discovered targets. | `name`, `website`, `job_url`, `raw_job_text`, **`status`**, `fit_score` |
| `research` | Enrichment per company (1:1). | `funding_stage`, `tech_stack[]`, `hiring_manager_name/linkedin/email`, `recent_news`, `fit_reasoning` |
| `messages` | Drafted/sent outreach per company (1:N). | `channel`, `subject`, `draft_body`, **`status`**, `conversation_id`, `sent_at`, `replied_at`, `followup_*` |
| `agent_log` | Append-only narration of every agent action. | `agent`, `action`, `detail`, `created_at` |

### Company status lifecycle
```
discovered → researched → draft_ready → approved → sent → replied
     │                                      ▲
     └─► skipped_low_fit          (set by Telegram approval)
         skipped_by_user
```

`agent_log` is what powers the live "Agent activity" feed in the UI — every
meaningful step writes a row, and the frontend renders them as a timeline.

---

## 8. Tools (external integrations)

Each tool is a thin, defensive client. All of them fail soft (log + return empty)
so a single flaky provider never crashes the pipeline.

| Tool | Role | Notes |
|---|---|---|
| **Tavily** (`tavily_client`) | Web search for discovery + research | Synchronous SDK wrapped in `asyncio.to_thread` to keep the event loop free |
| **Gemini** (`gemini_client`) | Research synthesis, fit scoring, drafting | Model name via `GEMINI_MODEL` env. Robust JSON extractor handles markdown fences / stray prose |
| **GLiNER2 / Pioneer** (`gliner_client`) | Structured entity extraction from job text | Calls Pioneer's hosted `POST /inference` over HTTP — **no local torch**, keeping the image small. Deterministic structured output |
| **Unipile** (`unipile_client`) | LinkedIn DM + reply checking | Region-specific DSN via `UNIPILE_DSN`. Requires a connected LinkedIn account |
| **Resend** (`unipile_client`) | Transactional email | HTTP API via httpx; `RESEND_FROM_EMAIL` must be a verified domain |
| **Telegram** (`telegram_client` + `tg/bot`) | Human approval gate | Outbound messages with inline keyboards; inbound callbacks resume the loop |

---

## 9. Frontend

A calm, editorial, **warm-monochrome ("stone")** interface — off-white paper,
ink-black type, Figtree font, Phosphor icons, no loud color.

- **`/` (landing):** the story. Word-reveal headline, a Lottie "signal reaching
  out" animation, a "how it works" 5-agent strip, and a CTA into the dashboard.
- **`/dashboard`:** the live cockpit. Animated stat counters
  (Discovered / Drafted / Sent / Replies), a pipeline board grouping companies by
  status with fit-score rings, a live agent-activity timeline, and the Run Hunt
  button. Polls the backend every 4 seconds.
- **`/setup`:** the profile form. Captures who you are, your stack, dealbreakers,
  bio, **the projects you have built**, and your GitHub/portfolio/LinkedIn links
  — so outreach can reference real work.

`lib/api.ts` centralizes all fetches: `cache: 'no-store'` (so the live pipeline
never looks frozen), try/catch around every call (so a backend hiccup during
polling never throws), and UTC timestamp normalization (so "time ago" is correct
regardless of timezone).

---

## 10. Request / Control Flow (end to end)

```
1. User fills /setup       ──► POST /api/profile          ──► user_profile row
2. User clicks "Run Hunt"  ──► POST /api/run              ──► run_discovery() task
3. Discovery               ──► Tavily + GLiNER2           ──► companies (discovered)
4. Orchestrator per company:
     research               ──► Tavily + Gemini           ──► research + fit_score
     (fit ≥ 7) outreach     ──► Gemini                    ──► message (pending)
     send_approval_request  ──► Telegram                  ──► [PAUSE]
5. User taps ✅ on phone    ──► tg/bot handle_callback     ──► message/company approved
6. Orchestrator resumes     ──► Delivery (Unipile/Resend) ──► message (sent)
7. Hourly follow-up task    ──► Unipile reply check        ──► notify / draft follow-up
8. UI polls every 4s        ──► GET /api/companies, /log   ──► live board + feed
```

---

## 11. Configuration & Secrets

All configuration is environment-driven via `pydantic-settings` (`config.py`).
**No secrets or account-specific values are hardcoded**. `DATABASE_URL` is
required for API startup. Third-party integration keys are optional at startup;
their clients skip outbound calls when not configured. See `.env.example` for
the full list.

Key variables: `GEMINI_API_KEY`, `GEMINI_MODEL`, `TAVILY_API_KEY`,
`UNIPILE_API_KEY`, `UNIPILE_ACCOUNT_ID`, `UNIPILE_DSN`, `RESEND_API_KEY`,
`RESEND_FROM_EMAIL`, `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`,
`PIONEER_API_KEY`, `PIONEER_MODEL_ID`, `DATABASE_URL`, `SYNC_DATABASE_URL`.

---

## 12. Running It

```bash
cp .env.example .env        # fill in your keys
docker compose up --build   # db + backend + frontend
```

- Frontend: http://localhost:3000
- Backend: http://localhost:8000 (`/health`, `/api/...`)
- Set your profile at `/setup`, then hit **Run Hunt**.

The backend uses **uv** (not pip) for Python deps. For local backend dev:
```bash
cd backend && uv sync && uv run uvicorn main:app --reload
```

> Schema is created with SQLAlchemy `create_all` (no migrations). When the data
> model changes, recreate the volume: `docker compose down -v && docker compose up --build`.

---

## 13. Design Decisions & Rationale

- **Shared-state over direct agent calls.** Agents coordinate through Postgres
  status fields, not function calls. This makes the system inspectable (every
  state is in the DB), resumable (the Telegram gate pauses and resumes cleanly),
  and fault-isolated (one agent failing doesn't cascade).
- **Human-in-the-loop by design.** The pipeline physically cannot send without an
  approval callback. Trust and safety are structural, not a config flag.
- **GLiNER2 via Pioneer's API, not local.** Running the model on Pioneer's
  infrastructure (vs. the local `gliner` PyPI package) removes a ~10GB
  torch/CUDA dependency, keeps the backend image ~1GB, and is the intended
  Pioneer integration.
- **Fail-soft tools.** Every external client logs and returns empty/raises
  narrowly on error, so a flaky provider degrades gracefully instead of crashing
  a run.
- **Async everywhere, blocking work offloaded.** Synchronous SDKs (Tavily,
  Gemini, SMTP-style work) run in threads so the asyncio event loop stays
  responsive under concurrent per-company pipelines.
- **uv + pinned lockfile + Python 3.13.** Reproducible, fast installs; a few
  dependency floors were chosen specifically for 3.13 compatibility
  (e.g. `asyncpg >= 0.30`, `sqlalchemy >= 2.0.36`).
- **Monochrome UI.** The interface stays out of the way; the story and the live
  pipeline are the focus.

---

## 14. Known Limitations / Future Work

- **Schema migrations.** Uses `create_all`; adopting Alembic would allow schema
  evolution without dropping the volume.
- **Approved follow-up sending.** The follow-up *draft + approval* flow exists;
  actually re-sending the approved follow-up is a natural next step.
- **LinkedIn recipient resolution.** Unipile's message endpoint expects a
  provider/internal ID; resolving a raw LinkedIn profile URL to that ID would
  make the LinkedIn path fully robust (email already works end to end).
- **Single-user.** The model assumes one `user_profile`; multi-tenant support
  would require scoping companies/messages per user.
- **Discovery query tuning.** Search templates are partially location/date
  hardcoded and could be fully derived from the profile.
