# M001-8itnlq Discussion Log

## Exchange — 2026-06-14T00:20:21.668Z

### Output

For M001, what should the concrete output be?

- **Options plus first build (Recommended)** — Audit the report/docs, map the opportunity space, then implement the highest-leverage first improvement.
- **Options only** — Produce a rigorous improvement map and roadmap without changing product code yet.
- **Build-first sprint** — Use the report/docs quickly, choose aggressively, and spend most of M001 on implementation.

**Selected:** None of the above
**Notes:** We have to read these docs now, the milestone already would have instrutions from us

### Breadth

How broad should the option generation be before we choose what to build?

- **Broad then rank (Recommended)** — List many plausible improvements, then rank by impact, feasibility, and demo value.
- **Only practical wins** — Ignore speculative ideas and focus on what can be implemented soon in this repo.
- **Creative stretch** — Include bold/novel ideas even if some become later milestones.

**Selected:** None of the above
**Notes:** You did not get it, I want you now extensively check these documents and we already can talk about the possibple options how we can make the system better

### Sources

What should count as source material for this milestone?

- **Report and docs (Recommended)** — Use deep-research-report.md and docs/ as authoritative, with codebase context for feasibility.
- **All repo material** — Also inspect README, architecture docs, workflows, and existing implementation before deciding.
- **Provided resources only** — Stay focused on the report/docs and avoid broader repo interpretation unless needed.

**Selected:** None of the above
**Notes:** As usual we already need to have an idea now what will be implemented
---

## Exchange — 2026-06-14T00:26:50.621Z

### Evidence

How should M001 store the evidence/resource trail?

- **Structured events (Recommended)** — Create resource/evidence records per company so Tavily, Pioneer, Gemini, and approvals are traceable over time.
- **Company fields** — Add evidence fields directly to the company record for a faster, simpler implementation.
- **Frontend-only view** — Avoid persistence changes and display evidence already available from current API responses where possible.

**Selected:** Structured events (Recommended)

### UI Surface

Where should the evidence become visible to the user first?

- **Company dossier (Recommended)** — Add a clear per-company evidence panel/drawer that explains source, entities, fit reasoning, and draft hook.
- **Cards and feed** — Add resource badges and concise evidence snippets directly to cards and the activity feed.
- **Approval screen** — Focus the evidence UI around the Telegram/approval moment so the user understands what they are approving.

**Selected:** Company dossier (Recommended)

### fal

How should fal fit into M001 architecture?

- **Optional dossier visual (Recommended)** — Add a stable optional visual artifact only after evidence is structured; do not make it required for core flow.
- **Defer fal** — Keep M001 focused on evidence, traceability, and resource visibility; leave fal for a later creative milestone.
- **Make fal central** — Treat generated visual/company artifacts as a main M001 feature and design the evidence model around them.

**Selected:** Optional dossier visual (Recommended)
---

## Exchange — 2026-06-14T00:27:09.965Z

### Arch Gate

Does this capture the architecture? Adjust anything before we move on.

- **Yes, continue (Recommended)** — Proceed to error handling with structured evidence events, company dossiers, and optional fal visuals.
- **Adjust architecture** — Pause here and change one or more architecture choices before continuing.

**Selected:** Yes, continue (Recommended)
---

## Exchange — 2026-06-14T00:27:30.876Z

### Errors

We can go deep on error handling and failure modes, or I can apply sensible defaults based on the architecture decisions above. Which do you prefer?

- **Sensible defaults (Recommended)** — Use pragmatic defaults: persist partial evidence, show source failures clearly, retry safe reads, and never block approval on optional fal.
- **Go deep now** — Spend another round detailing component failures, retries, timeouts, partial data, and user-facing diagnostics.

**Selected:** Sensible defaults (Recommended)
---

## Exchange — 2026-06-14T00:27:41.058Z

### Err Gate

Does this capture how errors should be handled? Adjust anything before we move on.

- **Yes, continue (Recommended)** — Proceed with partial evidence, clear diagnostics, conservative retries, and optional fal fallback behavior.
- **Adjust errors** — Pause and change failure behavior before quality planning.

**Selected:** Yes, continue (Recommended)
---

## Exchange — 2026-06-14T00:28:06.491Z

### Proof

What proof level should M001 target for the evidence/dossier upgrade?

- **Tested local flow (Recommended)** — Backend tests, frontend lint/typecheck, and a locally verifiable dashboard flow using seeded or mocked external evidence.
- **Live API proof** — Also exercise real Tavily/Gemini/Pioneer/fal calls if credentials exist, while keeping tests mocked.
- **Static proof only** — Verify files, wiring, lint/build, and screenshots/manual review but avoid deeper automated tests.

**Selected:** Tested local flow (Recommended)

### Done

What should be considered the must-have user-visible outcome?

- **Auditable dossier (Recommended)** — A user can inspect a company and understand sources, extracted facts, fit reasoning, draft hook, and approval state.
- **Judge resource story** — The most important outcome is that judges can clearly see how each hackathon resource contributes.
- **Approval confidence** — The most important outcome is that the user can confidently approve or reject outreach from evidence.

**Selected:** Auditable dossier (Recommended)

### CI Scope

How much CI/security maturity should be included in M001?

- **Targeted checks (Recommended)** — Add or update checks directly needed for the new backend/frontend evidence flow.
- **Broad hardening** — Spend more of M001 fixing CI, dependency review, docs drift, and security-policy gaps from the research report.
- **Defer maturity** — Keep M001 almost entirely product-facing and leave CI/security improvements for later.

**Selected:** Targeted checks (Recommended)
---

## Exchange — 2026-06-14T00:28:17.628Z

### QA Gate

Does this capture the quality bar? Adjust anything before we move on to requirements and roadmap?

- **Yes, continue (Recommended)** — Proceed to requirements and roadmap using the auditable dossier as the must-have outcome.
- **Adjust quality** — Pause and change acceptance criteria, tests, or CI/security scope.

**Selected:** Yes, continue (Recommended)
---

## Exchange — 2026-06-14T00:28:32.958Z

### Depth Check

Did I capture the depth right?

- **Yes, you got it (Recommended)** — Proceed to focused requirements and roadmap preview from this understanding.
- **Not quite** — Pause so you can clarify what is missing or wrong.

**Selected:** Yes, you got it (Recommended)
---

## Exchange — 2026-06-14T00:29:30.251Z

### Reqs

Confirm, adjust, or add to these requirements?

- **Confirm (Recommended)** — Use these requirements as the capability contract for the roadmap preview.
- **Adjust requirements** — Pause so you can clarify missing, wrong, or mis-owned requirements.
- **Add requirements** — Pause so you can add important capabilities before roadmap planning.

**Selected:** Confirm (Recommended)
---

## Exchange — 2026-06-14T00:29:49.393Z

### Roadmap

Ready to write, or want to adjust?

- **Ready to write (Recommended)** — Create the M001 planning artifacts from this roadmap preview.
- **Adjust roadmap** — Pause and change slices, ordering, risk, or definition of done before writing.

**Selected:** Ready to write (Recommended)
---

