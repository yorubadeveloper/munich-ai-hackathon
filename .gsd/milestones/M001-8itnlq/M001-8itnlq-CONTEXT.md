# M001-8itnlq: Auditable Resource Dossier

**Gathered:** 2026-06-14
**Status:** Ready for planning

## Project Description

HuntAgent is a human-approved multi-agent job-outreach system. This milestone makes the current system more qualitative by turning company recommendations and outreach drafts into auditable, resource-attributed dossiers. The user should see how Tavily, Pioneer/GLiNER2, Gemini, Telegram, and optionally fal contributed before trusting a recommendation or approving outreach.

The user’s framing is important: they asked to read `deep-research-report.md` and `docs/` to generate “all possible options” for making the current system better, creatively use provided hackathon resources, and resolve the problem more qualitatively. The chosen M001 context is not a generic dashboard polish task; it is an evidence, trust, and hackathon-resource visibility upgrade.

## Why This Milestone

The current system already has the right product shape: discover companies, research them, score fit, draft outreach, and require human approval. The research documents identify the stronger next move: make the resource chain visible and auditable so the system feels trustworthy rather than black-box.

M001 exists because “better outreach” should mean the user can inspect the sources, extracted facts, reasoning, and approval context behind each draft.

## User-Visible Outcome

### When this milestone is complete, the user can:

- Open a company in the dashboard and inspect a dossier showing Tavily sources, Pioneer extracted entities, Gemini reasoning/fit score, outreach hook, approval state, and resource labels.
- Review outreach with enough evidence to decide whether to approve, reject, or distrust the draft.
- See partial or failed resource contributions honestly instead of seeing a polished but unsupported recommendation.
- Optionally see a lightweight fal-style visual dossier artifact if fal is available, without that artifact blocking the core flow.

### Entry point / environment

- Entry point: Next.js dashboard, backed by FastAPI endpoints.
- Environment: local dev / browser.
- Live dependencies involved: PostgreSQL, FastAPI, Next.js, Tavily, Gemini, Pioneer/GLiNER2, Telegram approval flow, optional fal.

## Completion Class

- Contract complete means: backend models/API responses expose structured dossier/evidence data; tests prove the contract using mocked or seeded evidence.
- Integration complete means: dashboard can render the dossier from backend data and preserve the Telegram approval boundary.
- Operational complete means: external-resource failures are visible and optional fal failure does not break the core dossier/review path.

## Final Integrated Acceptance

To call this milestone complete, we must prove:

- A company can accumulate structured resource/evidence events and expose them through a typed dossier API.
- The dashboard renders the dossier so a user can understand sources, extracted facts, fit reasoning, outreach hook, and approval state before approving outreach.
- Telegram/human approval remains mandatory before delivery.
- Optional fal output is additive only; lack of fal credentials or fal failure does not block company review.
- Backend tests and frontend checks pass for the new flow.

## Scope

### In Scope

- Structured evidence/resource events per company.
- Resource labels for Tavily, Pioneer, Gemini, Telegram, and optional fal.
- Typed FastAPI dossier API contract.
- Dashboard company dossier UI.
- Evidence-backed outreach review context.
- Partial-failure visibility for missing/failed resource contributions.
- Targeted backend/frontend verification for the new flow.
- Optional lightweight fal visual dossier support if stable.

### Out of Scope / Non-Goals

- Autonomous outbound sending without human approval.
- Broad uncontrolled crawling of every company website.
- Full Pioneer fine-tuning or evaluation suite.
- Full fal media workflow or LoRA/custom media training.
- Broad CI/security hardening beyond checks needed for M001.
- Rewriting the agent architecture from scratch.

## Architectural Decisions

### Structured evidence events per company

**Decision:** Persist resource/evidence contributions as structured events associated with companies rather than only adding flat fields to the company object.

**Rationale:** The research/resource docs emphasize auditability and resource visibility. Structured events allow the dossier to show which resource produced which artifact, preserve partial progress, and support timeline-like inspection.

**Evidence:** `docs/hackathon-resource-map.md` recommends resource badges and an evidence trail; FastAPI docs support typed response models and tested API contracts.

**Alternatives Considered:**
- Flat company fields — faster, but weak for multiple resource contributions and timeline visibility.
- Frontend-only labels — lowest risk, but not durable or auditable.

### Company dossier as the first user-facing surface

**Decision:** The first visible UI surface should be a company dossier rather than only badges on cards or an approval-only Telegram view.

**Rationale:** The user wants a qualitative improvement to the current system. A dossier gives enough space to show sources, entities, reasoning, hooks, approval state, and failures in one reviewable place.

**Evidence:** The hackathon resource map says judges should see how web evidence becomes human-approved action.

**Alternatives Considered:**
- Cards/activity feed only — useful for visibility but too shallow for trust.
- Approval-only screen — useful at send time but misses earlier company evaluation.

### fal is optional and additive

**Decision:** fal may generate or represent a lightweight visual dossier artifact, but fal is not required for the core flow.

**Rationale:** The docs identify fal as the main missing creative layer but warn that it should only become core if stable. The auditable evidence trail must work without media generation.

**Evidence:** `docs/hackathon-resource-map.md` recommends deciding whether fal is core or submission-note; the selected answer was optional dossier visual.

**Alternatives Considered:**
- Defer fal entirely — safer, but loses a creative resource opportunity.
- Make fal central — more novel, but too risky for the first quality milestone.

### Partial failures are visible, not hidden

**Decision:** Missing or failed Tavily/Pioneer/Gemini/fal contributions should appear as visible evidence/dossier states with contextual errors, not silent gaps.

**Rationale:** The system solves a trust problem; hiding failures would undermine the dossier.

**Alternatives Considered:**
- Fail the entire dossier when one resource fails — too brittle.
- Hide failed sections — misleading and less debuggable.

## Error Handling Strategy

Use sensible defaults:

- Persist partial evidence/resource progress where possible.
- Show missing or failed resource contributions clearly in the dossier/activity state.
- Retry safe external reads conservatively where existing client patterns support it.
- Never log secrets or expose API keys in errors.
- Treat fal as optional: no fal credentials or fal generation failure must not block company review.
- Preserve Telegram/human approval as a hard gate before delivery.
- Record failed delivery separately from approval so the user can distinguish “approved” from “sent.”

## Risks and Unknowns

- Existing data model shape may not have a clean place for evidence events — this affects S01 implementation complexity.
- Current API may not expose enough company/research fields for a dossier — S02 retires this by creating a typed contract.
- UI surface may need careful design to avoid becoming noisy — S03 retires this with a focused dossier view.
- fal integration may be unstable or credentials may be unavailable — S04 keeps it optional.
- Tests may require stubbing external clients cleanly — S05 verifies local proof with mocked/seeded evidence.

## Existing Codebase / Prior Art

- `deep-research-report.md` — identifies high-priority gaps around repository maturity, testing, CI, security, documentation drift, and the need for operational trust.
- `docs/hackathon-resource-map.md` — maps Gemini, Pioneer, fal, Tavily, Aikido, and other resources to HuntAgent’s demo/submission story.
- `backend/tools/tavily_client.py` — current Tavily integration for search/research evidence.
- `backend/tools/gemini_client.py` — current Gemini integration for relevance, synthesis, scoring, contact selection, outreach, and follow-ups.
- `backend/tools/gliner_client.py` — current Pioneer/GLiNER2 extraction path.
- `backend/tg/bot.py` and `backend/tools/telegram_client.py` — existing approval/delivery notification surfaces.
- `frontend/components/CompanyCard.tsx`, `frontend/components/ActivityFeed.tsx`, `frontend/components/PipelineBoard.tsx` — likely dashboard integration surfaces for dossier visibility.

## Relevant Requirements

- R001 — Dossier advances auditable company review.
- R002 — Resource events make hackathon resources visible.
- R003 — Outreach review becomes evidence-backed.
- R004 — Dashboard exposes evidence, not just logs.
- R005 — Human approval remains mandatory.
- R006 — Partial failures are visible.
- R007 — Tested local flow proves the implementation.
- R008 — Optional fal visual adds creative resource value without blocking core flow.

## Technical Constraints

- Backend verification should use `uv run pytest` from `backend/`.
- Backend linting should use `uv run ruff check .` and formatting should follow existing Ruff conventions.
- Frontend verification should use available `frontend/package.json` scripts such as lint/typecheck/build where present.
- External clients must be mocked/stubbed in automated tests where possible.
- Secrets must remain in environment configuration and must never be logged.
- Pipeline states and Telegram approval contract must not be weakened.

## Integration Points

- PostgreSQL — persists companies, pipeline state, and new evidence/resource data.
- FastAPI — exposes the typed company dossier API.
- Next.js dashboard — renders the dossier and resource labels.
- Tavily — supplies search/source evidence.
- Pioneer/GLiNER2 — supplies structured entity extraction.
- Gemini — supplies reasoning, fit score, contact selection, outreach hook/draft.
- Telegram — remains the human approval gate.
- fal — optional visual dossier artifact only.

## Testing Requirements

- Backend unit/API tests for evidence event persistence/serialization and dossier API response shape.
- Tests or fixtures proving partial evidence/failure states are represented clearly.
- Tests or assertions that approval/delivery state is not advanced without human approval.
- Frontend lint/typecheck and, where practical, component/render verification for dossier display.
- Local verification should work with seeded/mocked evidence when live resource credentials are unavailable.

## Acceptance Criteria

- S01: Structured evidence/resource data can be stored or derived per company with resource, artifact type, payload, status, and timestamp.
- S02: FastAPI exposes a typed company dossier response that includes evidence events, resource labels, fit reasoning, outreach hook, approval state, and failure/partial states.
- S03: Dashboard renders a company dossier where the user can inspect Tavily sources, Pioneer entities, Gemini reasoning, draft hook, and approval state.
- S04: Approval review remains human-gated and optional fal visual output is additive; fal failure does not block dossier review.
- S05: Backend tests and frontend checks pass, and the local demo proves the resource story from evidence to approval context.

## Open Questions

- Whether existing database models should use a new evidence table or an existing JSON field — current thinking: prefer a dedicated structured event model if feasible.
- Whether fal should call the live API in M001 or expose a stable placeholder/contract until credentials are present — current thinking: live only if stable, otherwise optional contract/UI state.
- Whether company dossier should be a drawer, detail page, or expanded card — current thinking: choose the smallest UI surface that can show evidence clearly.
