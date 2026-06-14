---
depends_on: [M001-8itnlq, M002-qqpa83]
---

# M003-n9ygqi: Creative Media and Submission Polish

**Gathered:** 2026-06-14
**Status:** Ready for planning

## Project Description

M003 turns fal from an optional visual layer into a core generative media feature: visual opportunity dossier cards generated from the evidence trail and displayed in the dashboard. It also adds lightweight repo hardening (security policy, dependency review, Dependabot, docs drift fixes) and packages the full hackathon resource narrative for submission. This milestone explicitly targets the fal side challenge ($1000 fal credits).

Aikido is already connected to the repository and checks every PR to main. No Aikido setup, scanning, or remediation work is needed in M003.

## Why This Milestone

The fal side challenge requires generative media as a main feature, not a footnote or plain LLM endpoint. M001 made fal optional/additive; M003 promotes it to a core feature by generating visual opportunity cards from structured evidence. The submission narrative needs all hackathon resources visibly contributing: Tavily scouts, Pioneer extracts, Gemini reasons, fal visualizes, Aikido secures, and Telegram gates.

## User-Visible Outcome

### When this milestone is complete, the user can:

- See a fal-generated visual opportunity dossier card for each company in the dashboard dossier.
- Share or inspect the visual card as a summary of the company opportunity (name, role, key facts, fit score, outreach angle).
- Trust that the repo has basic security policy files and dependency review practices.
- Read a clear submission narrative explaining each resource's role in the system.

### Entry point / environment

- Entry point: Next.js dashboard (visual card in dossier), backend tool client for generation, submission docs.
- Environment: local dev / browser.
- Live dependencies involved: fal API, PostgreSQL (evidence persistence), M001 dossier API and dashboard.

## Completion Class

- Contract complete means: fal client generates visual cards from evidence data, with pytest coverage using mocked fal responses. Hardening files exist.
- Integration complete means: generated cards are stored as evidence events and visible in the dashboard dossier.
- Operational complete means: fal unavailability is handled gracefully via circuit breaker; the dossier works without the visual card.

## Final Integrated Acceptance

To call this milestone complete, we must prove:

- fal generates a visual opportunity dossier card from structured evidence trail data using Flux.1.
- The card is visible in the dashboard company dossier, with the image URL stored in PostgreSQL.
- fal failure does not block the core dossier or approval flow.
- SECURITY.md, Dependabot config, and dependency-review workflow are present.
- README version drift is fixed.
- The submission narrative accurately describes each resource's role.
- The fal integration is substantial enough for the fal side challenge (generative media as a core feature).

## Architectural Decisions

### fal client as backend tool

**Decision:** Add `backend/tools/fal_client.py` following the same pattern as `gemini_client.py` and `gliner_client.py`.

**Rationale:** Consistency with existing tool conventions. Backend generation keeps the frontend a consumer. Circuit breaker pattern handles API unavailability gracefully.

**Alternatives Considered:**
- Frontend-side generation — violates the backend-owns-resources pattern and complicates credential management.
- Batch script — disconnected from the evidence pipeline.

### Visual opportunity dossier card as the fal feature

**Decision:** Generate a visual summary card showing company name, role, key facts, fit score, and outreach angle from evidence trail data.

**Rationale:** This is the most natural creative use of fal within HuntAgent: turning structured evidence into a visual artifact. It meets the side challenge criteria (generative media as core feature) without overreaching into video/audio.

**Alternatives Considered:**
- Video summaries — higher novelty but much higher complexity and latency.
- Audio narration — less visual impact for a dashboard product.

### Fal Model Selection

**Decision:** Use Flux.1 for generating the visual dossier cards.

**Rationale:** Flux.1 offers high quality, handles text well, and is great for structured dossier cards.

**Alternatives Considered:**
- SDXL / SD3 — fast and reliable, but text rendering may be less optimal for data-heavy cards.

### Card Visual Style

**Decision:** Style the cards as a "Modern Tech Dossier".

**Rationale:** Clean typography and a dashboard-native look ensure the card is easy to read and fits seamlessly into the existing Next.js frontend.

**Alternatives Considered:**
- Minimalist Data Summary or Cyberpunk/Retro — rejected in favor of a clean, modern aesthetic.

### Image Storage Strategy

**Decision:** Store the image URL provided by fal directly in the database.

**Rationale:** This is the simplest implementation and efficiently manages fal credits without needing complex file downloading and local storage overhead.

**Alternatives Considered:**
- Download and store locally — safer against URL expiration but adds complexity.
- Re-generate on demand — risks exhausting the $25 credit voucher.

### Aikido removed from M003 scope

**Decision:** No Aikido work in M003. Aikido is already connected to the repository and checks every PR to main.

**Rationale:** User confirmed Aikido is operational. Adding redundant setup would waste effort.

### Lightweight hardening before submission

**Decision:** Add SECURITY.md, CONTRIBUTING.md, LICENSE, Dependabot config, dependency-review action, and fix README version drift.

**Rationale:** These are low-effort improvements that directly improve repo maturity and are visible to any reviewer. They do not depend on Aikido.

**Alternatives Considered:**
- Defer entirely — cheap improvements left on the table.

## Error Handling Strategy

- fal API unavailable → circuit breaker trips (same pattern as `gliner_client.py`); dossier works without the visual card; failure state shown honestly in the dossier.
- Card generation produces unexpected output → log and skip; never block core dossier or approval.
- `FAL_API_KEY` not configured → graceful skip, card generation disabled, dossier remains functional.
- Hardening files are static additions — no runtime error surface.
- Demo narrative is documentation — no failure mode.

## Risks and Unknowns

- fal API stability and latency for image generation — could affect demo reliability.
- Card visual quality depends on prompt engineering and fal model capabilities — may need iteration.
- fal credits budget ($25 voucher) — generation should be efficient enough to avoid exhausting credits during development/demo.
- Side challenge judges may interpret "core feature" strictly — the card must be clearly integrated into the product flow, not a bolted-on demo.

## Existing Codebase / Prior Art

- `backend/tools/gemini_client.py` — pattern for the fal client (async, circuit breaker, safe HTTP, config-driven).
- `backend/tools/gliner_client.py` — same pattern, closest analog for a media/extraction API client.
- `backend/config.py` — needs `fal_api_key` added.
- `.env.example` — already contains `FAL_API_KEY=` placeholder.
- `docs/hackathon-resource-map.md` — fal section describes platform capabilities, side challenge criteria, demo framing, and implementation notes.
- M001 evidence trail and dossier surface — the card generation input and display target.

## Relevant Requirements

- R008 — Optional fal dossier visual (M001 made it optional; M003 promotes it to core).
- R010 — Full fal media workflow (this milestone partially activates it as visual card generation).
- R011 — Broad CI/security hardening (partially activated: lightweight hardening only).
- R001 — Auditable company dossier (visual card enriches the dossier).
- R002 — Resource attribution trail (fal becomes a visible resource contributor).

## Scope

### In Scope

- `backend/tools/fal_client.py` with circuit breaker and `FAL_API_KEY` config.
- Visual opportunity dossier card generation from evidence trail data using Flux.1.
- Card URL stored as evidence event (resource: `fal`) and displayed in dashboard dossier.
- SECURITY.md, CONTRIBUTING.md, LICENSE if missing.
- Dependabot config for Python and Node.
- dependency-review GitHub Action.
- README version drift fix.
- Submission narrative text and resource-role framing.
- pytest for fal client with mocked responses.

### Out of Scope / Non-Goals

- Aikido setup, scanning, or remediation (already operational).
- Full fal media workflows, LoRA training, video, or audio.
- Production deployment or cloud infrastructure.
- Agent pipeline logic changes.
- Pioneer model changes (M002).
- Deep CI overhaul or code-scanning workflows.
- Downloading fal images for local storage.

## Technical Constraints

- fal client should use `uv run` from `backend/`.
- Tests use `uv run pytest` from `backend/`.
- fal API calls mocked in tests; real calls only when `FAL_API_KEY` is configured.
- Card generation must be efficient enough to work within the $25 fal credits voucher.
- No secrets in logs or evidence events.

## Integration Points

- fal API — image generation for visual dossier cards.
- M001 evidence trail — structured input for card generation.
- M001 dossier API — card surfaces through the same typed response.
- M001 dashboard — card rendered in company dossier.
- PostgreSQL — evidence event persistence for generated cards.
- GitHub — hardening files, Dependabot, dependency-review action.

## Testing Requirements

- pytest for `fal_client.py` with mocked fal API responses.
- Circuit breaker and graceful skip behavior tested.
- Frontend lint/typecheck for card display components.
- Hardening files verified to exist.
- Submission narrative reviewed for accuracy against actual resource usage.

## Acceptance Criteria

- fal client generates a visual opportunity card from evidence trail data using Flux.1.
- Generated card is stored as an evidence event (URL) and displayed in the dashboard dossier.
- fal failure is non-blocking: dossier works without the visual card.
- SECURITY.md, Dependabot config, and dependency-review workflow are present.
- README version references match actual dependencies.
- Submission narrative describes each resource's role accurately.
- fal integration is substantial enough for the side challenge: generative media as a core feature.

## Open Questions

- Card visual design and prompt engineering — current thinking: iterate during implementation; use a clean data-to-image prompt tailored for the "Modern Tech Dossier" style.