---
id: M003-n9ygqi
status: ready
---

# M003-n9ygqi: Creative Media and Submission Polish

**Gathered:** 2026-06-15
**Status:** Ready for planning

## Project Description

M003 turns fal from an optional visual layer into a core generative media feature: visual opportunity dossier cards generated from the evidence trail and displayed in the dashboard. It also adds lightweight repo hardening (security policy, dependency review, Dependabot, docs drift fixes) and packages the full hackathon resource narrative for submission. This milestone explicitly targets the fal side challenge ($1000 fal credits). Aikido is already connected to the repository and checks every PR to main. No Aikido setup, scanning, or remediation work is needed in M003.

## Why This Milestone

The fal side challenge requires generative media as a main feature, not a footnote or plain LLM endpoint. Promoting fal to automatically generate a judge-readable visual opportunity card after research completes ensures it is a core feature. The submission narrative needs all hackathon resources visibly contributing.

## User-Visible Outcome

### When this milestone is complete, the user can:

- See an automatically generated fal visual opportunity dossier card for each company in the dashboard dossier, acting as a clean summary of company, role, fit, key facts, and outreach angle.
- Rely on the dossier degrading quietly and remaining usable with a calm "Visual card unavailable" status if fal is slow, missing a key, or fails.
- Trust that the repo has basic security policy files and dependency review practices.
- Read a clear submission narrative explaining each resource's role in the system.

### Entry point / environment

- Entry point: Next.js dashboard (visual card in dossier), backend tool client for generation, submission docs.
- Environment: local dev / browser.
- Live dependencies involved: fal API, PostgreSQL (evidence persistence), M001 dossier API and dashboard.

## Completion Class

- Contract complete means: fal client generates visual cards from evidence data, mocked fal backend tests pass, and hardening files exist.
- Integration complete means: generated cards are automatically stored as evidence events (URL reused per company to save credits) and visible in the dashboard dossier without breaking the flow.
- Operational complete means: fal unavailability is handled gracefully via circuit breaker; the dossier works quietly without the visual card.

## Final Integrated Acceptance

To call this milestone complete, we must prove:

- A seeded/demo company dossier shows the fal card in the browser (Browser dossier proof).
- fal failure does not block the core dossier or approval flow, showing quiet degraded status.
- Card generation happens automatically after research, but only once per company (reusing the stored URL) unless explicitly regenerated, conserving credits.
- SECURITY.md, Dependabot config, and dependency-review workflow are present.
- README version drift is fixed.
- The submission narrative accurately describes each resource's role.
- Frontend lint and typechecks pass.

## Architectural Decisions

### Auto-generation and Core Feature Shape

**Decision:** Generate the card automatically after evidence exists, store it as a fal evidence event, and render it in the dossier by default.

**Rationale:** This creates the strongest "core feature" story for the side challenge. If fal fails, the dossier still works with an honest status.

**Alternatives Considered:**
- Generate on demand — More control and fewer credits, but feels slightly less automatic/core.
- Demo-only golden path — Lower implementation risk, but may feel bolted-on.

### Card Usage Optimization

**Decision:** Prioritize a clean, instantly understandable, judge-readable card that summarizes company, role, fit, key facts, and outreach angle.

**Rationale:** This directly answers "Who is this company?", "Why is it a fit?", and "What did the agent learn?", providing immediate value in the dossier.

**Alternatives Considered:**
- Shareable artifact — More emphasis on layout and aesthetics, less dense dashboard text.
- Evidence companion — Emphasizing provenance/resource labels and confidence.

### Failure UX

**Decision:** Show a quiet degraded status in the dossier if fal fails, is missing a key, or is slow.

**Rationale:** The evidence trail and approval flow remain usable. The card slot displays a calm note like "Visual card unavailable" or "Generating visual card". This matches the prior non-blocking fal decision.

**Alternatives Considered:**
- Prominent retry action — Clear "Generate again" action, but slightly more UI/backend state scope.
- Hide failed card — Cleanest UI, but risks fal contribution disappearing from the visible product story.

### Credit Control

**Decision:** Generate once per company automatically, reuse the stored URL, and require explicit refresh for regeneration.

**Rationale:** Avoids burning through the $25 fal voucher while still making cards feel automatic.

**Alternatives Considered:**
- Demo allowlist — Auto only for seeded/flagged companies; strong demo safety but weaker "core feature" feel.
- Every research refresh — Freshest visual summary, but highest cost and latency risk.

### Milestone Scope Priority

**Decision:** Protect the fal side challenge implementation (visual-card generation, evidence persistence, dashboard display path, graceful fallback) above repo hardening extras if time gets tight.

**Rationale:** The fal integration is the primary differentiator for this side challenge.

**Alternatives Considered:**
- Submission package — Strong docs/screenshots, but may reduce feature depth.
- Repo hardening — Trustworthy repo hygiene, but less distinctive.

## Error Handling Strategy

- fal API unavailable → circuit breaker trips (same pattern as gliner_client.py); dossier works without the visual card, showing quiet degraded status.
- Card generation produces unexpected output → log and skip; never block core dossier or approval.
- FAL_API_KEY not configured → graceful skip, card generation disabled, dossier remains functional.
- Hardening files are static additions — no runtime error surface.
- Demo narrative is documentation — no failure mode.

## Risks and Unknowns

- fal API stability and latency for image generation — mitigated by quiet degraded status.
- Card visual quality depends on prompt engineering and fal model capabilities — mitigated by focusing on a judge-readable summary layout.
- fal credits budget ($25 voucher) — mitigated by generate-once-per-company policy.
- Side challenge judges may interpret "core feature" strictly — mitigated by automatic post-research generation and dossier integration.

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
- Auto-trigger card generation after research completes.
- Ensure generation happens only once per company (reuse URL).
- Card URL stored as evidence event (resource: `fal`) and displayed in dashboard dossier.
- Quiet degraded status UI for fal failures.
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

- fal generates a visual opportunity card automatically after company evidence exists and stores/reuses one URL per company.
- The dashboard dossier renders the judge-readable card and quietly degrades when fal is missing, slow, or unavailable.
- Browser dossier proof, mocked backend tests, frontend lint/typecheck, and submission docs verify the feature.
- Lightweight hardening and submission narrative are completed without adding Aikido setup scope.

## Open Questions

- Card visual design and prompt engineering — current thinking: iterate during implementation; use a clean data-to-image prompt tailored for the "Modern Tech Dossier" style.