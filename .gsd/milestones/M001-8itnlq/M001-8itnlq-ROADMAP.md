# M001-8itnlq: Auditable Resource Dossier

**Vision:** Make HuntAgent’s company recommendations explainable and judge-visible by turning Tavily, Pioneer, Gemini, Telegram, and optional fal contributions into an auditable resource dossier.

## Success Criteria

- User can inspect why a company is recommended before approving outreach.
- Dashboard shows source evidence, extracted entities, Gemini fit reasoning, outreach hook, approval state, and resource labels.
- Optional fal visual output is additive and does not block the core review flow.
- Partial external-resource failures are visible rather than silently hidden.
- Targeted backend/frontend verification proves the new evidence flow locally.

## Slices

- [x] **S01: Evidence Trail Backbone** `risk:high` `depends:[]`
  > After this: A company can expose structured resource/evidence events for sources, entities, reasoning, and draft hooks through backend data structures or persistence.

- [x] **S02: Dossier API Contract** `risk:high` `depends:[S01]`
  > After this: The dashboard can request a typed company dossier containing evidence, resource labels, fit reasoning, outreach hook, approval state, and partial-failure data.

- [ ] **S03: Dashboard Company Dossier** `risk:medium` `depends:[S02]`
  > After this: A user can open a company dossier and inspect Tavily sources, Pioneer entities, Gemini reasoning, the outreach hook, approval state, and resource labels.

- [ ] **S04: Approval and Optional Visual Layer** `risk:medium` `depends:[S03]`
  > After this: The review flow preserves Telegram approval and can show optional fal-style visual output without blocking core company review.

- [ ] **S05: Verification and Demo Readiness** `risk:low` `depends:[S04]`
  > After this: Local tests/checks prove the evidence flow, UI wiring, partial-failure behavior, and hackathon resource demo narrative.

## Boundary Map

### S01 → S02

Produces:
- Resource/evidence event shape with company association, resource name, artifact type, payload, status, timestamp, and error context where applicable.
- Fixture or model-level examples for Tavily source, Pioneer entity extraction, Gemini reasoning, Telegram approval state, and optional fal visual artifact.

Consumes:
- Existing company and agent state from the backend.

### S02 → S03

Produces:
- Typed company dossier API response containing company summary, evidence events, resource labels, fit reasoning, outreach hook, approval state, and partial-failure states.
- Backend tests or fixtures demonstrating the contract.

Consumes:
- S01 evidence/resource event shape.

### S03 → S04

Produces:
- Dashboard company dossier UI surface and client-side types/components for evidence/resource display.
- User-visible dossier sections for sources, entities, reasoning, outreach hook, approval state, and failures.

Consumes:
- S02 dossier API response.

### S04 → S05

Produces:
- Approval-context integration that preserves Telegram/human gate.
- Optional fal visual artifact state or integration that is non-blocking.
- Failure states showing optional media/resource unavailability honestly.

Consumes:
- S03 dossier UI and S02 dossier contract.
