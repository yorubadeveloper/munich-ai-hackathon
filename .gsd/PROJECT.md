# Project

## What This Is

HuntAgent is a single-user, human-approved, multi-agent job-outreach system. A Next.js dashboard talks to a FastAPI backend; agents discover target companies, research them, score fit, draft tailored outreach, and require Telegram approval before any outbound delivery.

M001-8itnlq upgrades the current system from “AI generated outreach exists” to “the user can inspect why the agent trusts a company and how each hackathon resource contributed.” The milestone is centered on an auditable company dossier and visible resource trail.

## Core Value

The one thing that must work even if everything else is cut: a user can inspect a company’s evidence, understand the fit reasoning, and approve or reject outreach without trusting a black-box draft.

## Project Shape

- **Complexity:** complex
- **Why:** The work crosses backend state, API contracts, frontend review UX, external AI/search resources, human approval, optional media generation, and test/demo readiness.

## Current State

The repository already contains the HuntAgent concept and implementation skeleton: FastAPI backend, Next.js frontend, PostgreSQL state, discovery/research/outreach/delivery/follow-up agents, Tavily search, Gemini reasoning and drafting, Pioneer/GLiNER2 extraction, Telegram approval, and safe outbound URL handling.

The research documents identify the main gap as product trust and operational maturity rather than the product idea. Hackathon resources are used, but their contributions need to become more visible and auditable in the user-facing flow.

## Architecture / Key Patterns

- Backend: Python 3.13, FastAPI, async SQLAlchemy/SQLModel-style data access, PostgreSQL, Pydantic settings.
- Frontend: Next.js App Router with React components for dashboard, pipeline board, company cards, status badges, and activity feed.
- AI/search resources: Tavily scouts and extracts live web evidence; Pioneer/GLiNER2 extracts structured entities; Gemini reasons, scores, selects contacts, and drafts outreach; fal is optional for visual dossier artifacts; Telegram remains the human approval gate.
- Key pattern for M001: persist structured evidence/resource events per company, expose a typed dossier API, render a company dossier in the dashboard, and make partial external-resource failures visible rather than silent.

## Capability Contract

See `.gsd/REQUIREMENTS.md` for the explicit capability contract, requirement status, and coverage mapping.

## Milestone Sequence

- [ ] M001-8itnlq: Auditable Resource Dossier — Make company recommendations explainable through structured evidence, resource attribution, dossier UI, approval context, optional fal visual output, and targeted verification.
- [ ] M002-qqpa83: Pioneer Evaluation and Model Quality — Build an evaluation pipeline comparing Pioneer/GLiNER2 vs Gemini extraction on synthetic data, conditionally fine-tune, and target the Fastino side challenge (€500). Depends on M001.
- [ ] M003-n9ygqi: Creative Media and Submission Polish — Promote fal to a core feature (visual opportunity dossier cards), add lightweight repo hardening, and package the submission narrative. Targets fal side challenge ($1000 credits). Depends on M001 and M002.
