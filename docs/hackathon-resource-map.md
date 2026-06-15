# Hackathon Resource Map

Status: prepared for the Tech: Europe Munich AI Hackathon on 2026-06-13.

This document explains how HuntAgent should present and use every hackathon
resource from the public manual for the selected Open Innovation track. It is
written as a practical demo and submission guide: what each resource can do,
where it is already used in this repository, how to make its role visible to
judges, and what to implement next if time allows.

## Source Scope

Primary event source:

- Public manual: https://techeurope.notion.site/munich-hack
- Manual title: `{Tech: Europe} Munich AI Hackathon Manual`
- Chosen track: `Open Innovation`
- Track challenge: `Build whatever you want`
- Track prize: `Qualification for the Finalist Stage (3x)`

Resource section in the manual:

- Google DeepMind - Frontier AI Models
- Pioneer by Fastino - Models that train themselves
- fal - Generative Media platform for developers
- Tavily - Real-time search, extraction, research, and web crawling through a single, secure API

Relevant side challenges in the manual:

- Fastino - Best use of Pioneer
- Aikido - Most Secure Build
- fal - Best use of fal

Operational links in the manual:

- Discord server: https://discord.gg/brSqTjJVdh
- Project submission form: https://tally.so/r/XxNqDd
- Venue: Tacto office, Sandstrasse 33, 80335 Munich

## Open Innovation Interpretation

The Open Innovation track is the correct home for HuntAgent because the product
is not a single-resource demo. It is a full agentic workflow: discover target
companies, research them, score fit, draft a tailored outreach message, request
human approval, deliver the message, and watch for follow-up opportunities.

The strongest submission story is:

> HuntAgent turns job hunting from a manual, repetitive process into an
> auditable multi-agent workflow. Each hackathon resource owns a distinct layer
> of the system: Tavily scouts the web, Pioneer reads job text into structured
> entities, Gemini reasons and writes, fal can turn the evidence into a visual
> artifact, and Aikido validates that the build is secure enough to trust.

The resources should not be treated as decorative badges. Judges should be able
to see where each one appears in the pipeline and why it is the right tool for
that step.

## Resource Summary

| Resource | Manual role | What it can do for HuntAgent | Current repo status | Best demo use |
| --- | --- | --- | --- | --- |
| Google DeepMind / Gemini | Frontier AI models, temporary accounts on site | Reason over noisy web data, extract JSON, score candidate-company fit, pick the best contact, write outreach and follow-ups | Implemented in `backend/tools/gemini_client.py`; configured through `GEMINI_API_KEY` and `GEMINI_MODEL` | Show fit reasoning, research synthesis, and a non-generic outreach draft |
| Pioneer by Fastino | Models that train themselves | Run schema-guided GLiNER2 extraction, fine-tune specialized models, generate synthetic data, evaluate against frontier models, use adaptive inference | Implemented for GLiNER2 inference in `backend/tools/gliner_client.py`; configured through `PIONEER_API_KEY` and `PIONEER_MODEL_ID` | Show entity extraction from raw job text: company, role, stack, stage, manager, salary, remote policy |
| fal | Generative media platform for developers | Generate images, video, audio, avatars, candidate/company visuals, and media workflows; deploy generative models through API, queues, webhooks, streaming, and realtime patterns | Not integrated in runtime yet; `.env.example` contains `FAL_API_KEY`, but `backend/config.py` and app code do not consume it yet | Add a visual "opportunity dossier" or personalized portfolio proof asset generated from approved company evidence |
| Tavily | Real-time search, extraction, research, and web crawling API | Search the live web, extract raw page content, crawl/map sites, and feed cited evidence into agents | Implemented in `backend/tools/tavily_client.py`; configured through `TAVILY_API_KEY` | Show how search results become discoverable companies and research evidence |
| Aikido | Most Secure Build side challenge | Scan code/repo security, dependencies, exposed secrets, and risk categories; provide a security report screenshot for submission | Not integrated in code; mentioned in `README.md`; repo has local SSRF-safe outbound URL validation | Connect the repo, capture the security report, and pair it with existing `safe_http` protections |

## Current HuntAgent Pipeline

The current codebase already gives three resources a real operational role:

1. Discovery uses Tavily to search profile-driven job and company queries.
2. Discovery uses Gemini to reject listicles, aggregators, and off-target pages.
3. Discovery uses Pioneer/GLiNER2 to extract structured job entities from raw text.
4. Research uses Tavily to collect funding, product, tech, news, and job-post evidence.
5. Research uses Gemini to synthesize company facts, score candidate fit, and pick the best contact.
6. Outreach uses Gemini to draft channel-specific LinkedIn or email copy.
7. Telegram gates the message before anything goes out.
8. Aikido should verify the repository before submission.
9. fal is the main missing creative layer and should be added only if it can be made visible and stable.

The most defensible product narrative is not "we used many APIs." It is "we
gave every resource a job in the agent team."

## Google DeepMind / Gemini

### Manual Offer

The manual lists Google DeepMind as a resource for frontier AI models. It also
states that temporary accounts are available on site and links to:

- https://goo.gle/hackathon-account

The finalist-stage prize section also lists Gemini credits for top finalist
placements. That is not the same as the initial on-site temporary account, but
it reinforces that Gemini should be visible in the demo and submission.

### Platform Capabilities

Gemini is the reasoning and generation layer. In HuntAgent terms, it can:

- Convert messy web-search results into a structured company profile.
- Return JSON for deterministic downstream processing.
- Score candidate-company fit against role, seniority, stack, location, funding stage, size, and dealbreakers.
- Decide whether a search result is a real target company or low-quality noise.
- Choose the best hiring contact from LinkedIn people-search candidates.
- Draft concise outreach for LinkedIn or email with strict voice and length rules.
- Draft follow-up messages when a company has not replied.
- Potentially support multimodal features later, such as document understanding for resumes or visual media analysis.

Gemini should be presented as the strategist: it does not fetch the evidence and
it does not own deterministic entity extraction. It interprets evidence,
applies judgment, and turns the result into a human-ready action.

### Current Implementation

Relevant files:

- `backend/tools/gemini_client.py`
- `backend/agents/discovery.py`
- `backend/agents/research.py`
- `backend/agents/outreach.py`
- `backend/agents/followup.py`
- `backend/config.py`

Configuration:

- `GEMINI_API_KEY`
- `GEMINI_MODEL`
- Default in `backend/config.py`: `gemini-3.5-flash`
- Default in `.env.example`: `gemini-3.5-flash`

Current functions:

- `check_relevance(...)`: rejects pages that are not a specific, on-target hiring company.
- `synthesise_research(...)`: creates funding, headcount, tech stack, manager, recent-news, and company-summary fields.
- `score_fit(...)`: returns reasoning plus a numeric score from 1.0 to 10.0.
- `pick_best_contact(...)`: chooses the best person to contact from verified candidates.
- `draft_outreach_message(...)`: writes the final outreach JSON.
- `draft_followup_message(...)`: writes short follow-up text.

Implementation details worth showing:

- Gemini calls are wrapped with `asyncio.to_thread(...)` so synchronous model calls do not block the async app loop.
- Responses pass through a defensive JSON extractor because model output can contain markdown fences or stray prose.
- Discovery defaults to keeping a result if the relevance-gate JSON parse fails, avoiding silent total data loss.
- Fit scoring includes explicit wildcard rules so unspecified user preferences are not penalized.

Note: `README.md` currently contains both `Gemini 2.0 Flash` in the stack section
and `Google Gemini 3.5 Flash` in the partner section. The config-backed value is
`gemini-3.5-flash`; demo narration should use that unless the README is cleaned
up separately.

### Artistic Use In The Demo

Frame Gemini as the "strategist and writer" inside the agent room.

Concrete demo beats:

- Show a noisy search result before filtering.
- Show Gemini's relevance reason for keeping or dropping it.
- Show the research profile Gemini synthesizes from Tavily evidence.
- Show the fit score and reasoning.
- Show the final outreach message, emphasizing that it uses a specific company hook rather than generic praise.

Best visible evidence:

- Activity feed entries from discovery and research.
- Stored research row fields: funding stage, headcount, tech stack, recent news, hiring contact.
- Outreach draft with `hook_used`.

### Risks And Guardrails

- Gemini can hallucinate if Tavily evidence is thin.
- JSON can be malformed; the repo already handles this defensively.
- Contact selection must remain grounded in verified LinkedIn candidates, not invented names.
- Outreach must stay human-approved before delivery.

Recommended guardrail for submission:

- In the UI or logs, label Gemini output as "reasoned from evidence" and show the evidence source where possible.

## Pioneer By Fastino

### Manual Offer

The manual lists Pioneer by Fastino as "Models that train themselves" and links
to a Munich hackathon onboarding page:

- https://wholesale-mackerel-22f.notion.site/Munich-Hackathon-Onboarding-3798413d4744807e8dcdc50f1cbc8419?source=copy_link

The manual also includes a Fastino side challenge:

- Side challenge: `Fastino - Best use of Pioneer`
- To compete: use Pioneer in the project and confirm it in the submission.
- Judges look for a fine-tuned model that outperforms or replaces a general-purpose LLM API call.
- They also look for thoughtful use of Pioneer's features: synthetic data generation, evaluation against frontier models, and adaptive inference.
- Bonus points: creative use of GLiNER2 and/or Gemma 4.
- Prize: 500 EUR.

### Platform Capabilities

Pioneer is the specialized-model layer. In HuntAgent terms, it can:

- Run GLiNER2-style named entity recognition against raw text.
- Extract fields with a schema instead of asking a frontier LLM to infer freeform JSON.
- Power small, task-specific models for repeatable extraction and classification.
- Fine-tune a model for this product's job-posting domain.
- Generate synthetic labeled examples when real labeled job data is limited.
- Evaluate a specialized model against Gemini or another frontier model.
- Use adaptive inference so simple extraction tasks do not always require a large general-purpose model.

Pioneer should be presented as the "entity lens": it sees the structured facts
inside raw job text before the strategist reasons over them.

### Current Implementation

Relevant files:

- `backend/tools/gliner_client.py`
- `backend/agents/discovery.py`
- `backend/config.py`

Configuration:

- `PIONEER_API_KEY`
- `PIONEER_MODEL_ID`

Current endpoint:

- `https://api.pioneer.ai/inference`

Current schema:

- `company_name`
- `job_title`
- `tech_stack`
- `company_stage`
- `hiring_manager`
- `salary`
- `remote_policy`

Current behavior:

- Discovery calls `extract_job_entities(...)` on raw Tavily result content.
- The app uses extracted company names as a grounded signal, alongside Gemini's relevance gate.
- Extracted fields appear in the activity feed when available.
- The client uses `safe_async_client(...)` and restricts outbound calls to `api.pioneer.ai`.
- If credentials or billing fail with `401`, `402`, or `403`, the client disables itself for the current run and falls back gracefully.

### Artistic Use In The Demo

Frame Pioneer as "the lens that turns prose into evidence."

Concrete demo beats:

- Start from a raw job post snippet.
- Show Pioneer extracting role, stack, remote policy, salary, or stage.
- Show the extracted fields feeding the discovery log.
- Show Gemini using the same structured facts to score fit and draft outreach.

This creates a clean division of labor:

- Tavily finds the page.
- Pioneer extracts job facts.
- Gemini decides whether the opportunity is worth action.

### Stronger Side-Challenge Path

If the team wants to compete seriously for `Best use of Pioneer`, the current
GLiNER2 extraction is a good base but not enough by itself. The side challenge
explicitly values fine-tuning, evaluation, synthetic data, and replacing a
general-purpose LLM call.

High-impact upgrade:

1. Collect 30 to 100 sample job snippets from Tavily results or seeded examples.
2. Label the target fields: company, title, stack, stage, manager, salary, remote policy.
3. Generate synthetic variants for missing labels and ambiguous wording.
4. Fine-tune a Pioneer model for HuntAgent job extraction.
5. Compare the fine-tuned model against Gemini extraction on the same samples.
6. Display the evaluation in the submission: accuracy, latency, cost, and cases where Pioneer replaces an LLM call.

Judging phrasing:

> We use Pioneer where deterministic extraction matters. Instead of asking a
> frontier model to repeatedly parse job text, HuntAgent uses a schema-guided
> GLiNER2/Pioneer pass, then gives the structured evidence to Gemini for higher
> level reasoning.

### Risks And Guardrails

- Missing `PIONEER_MODEL_ID` means the current extraction silently skips.
- A generic base model may miss domain-specific job-posting patterns.
- The best side-challenge claim requires an actual fine-tuned or evaluated model, not only API use.

## fal

### Manual Offer

The manual lists fal as a generative media platform for developers.

Hackathon access details in the manual:

- Code: `techeurope-munich`
- Voucher: http://fal.ai/coupon-claim/techeurope-munich
- Credits: `$25 worth of credits`

The manual also includes a fal side challenge:

- Side challenge: `fal - Best use of fal`
- To compete: use fal in the project and confirm it in the submission.
- Judges look for fal-powered generative media models in a core feature.
- They want creativity and advanced use, such as a LoRA, workflow, or genmedia CLI.
- The manual states that generative media needs to be the main feature for this side challenge; plain LLM endpoints do not count.
- Prize: `$1000 fal Credits`.

### Platform Capabilities

fal is the generative media layer. In HuntAgent terms, it can:

- Generate images for personalized candidate/company artifacts.
- Generate video clips for pitch intros, visual summaries, or demo transitions.
- Generate audio or voice content where appropriate.
- Use vision APIs and media workflows.
- Run model APIs behind queues, webhooks, streaming, or realtime flows.
- Host custom generative workflows when a simple one-shot image is not enough.

fal should be presented as the "visual storyteller": it turns the evidence
trail into something a human can inspect quickly.

### Current Implementation

Current status:

- No runtime fal client exists yet.
- `backend/config.py` does not define `fal_api_key`.
- `.env.example` currently contains `FAL_API_KEY=`, but the application ignores it unless config and code are added.
- No route, agent, worker, or UI component currently calls fal.

Because this is not implemented yet, the team should be precise in the demo:

- Do not claim that fal is already part of the live pipeline unless the integration is added.
- It is acceptable to describe fal as the planned or optional creative layer if time runs out.
- If competing for the fal side challenge, fal must become a core feature, not a background decoration.

### Recommended HuntAgent Use

Low-risk integration:

- Generate an "opportunity dossier cover" for each high-fit company.
- Inputs: company name, role, tech stack, recent news, and candidate project.
- Output: a clean visual card that appears in the dashboard before human approval.
- Purpose: help the user quickly understand why this company is worth contacting.

More ambitious integration:

- Generate a personalized portfolio proof asset for the target company.
- Example: a branded visual one-pager showing how the candidate's relevant project maps to the company's product challenges.
- The asset should be attached or linked only after human approval.

Side-challenge-grade integration:

- Make generative media central to the product experience.
- For example, each outreach recommendation creates a media artifact that is not possible through text alone: a company-specific visual pitch, generated portfolio card, or short product-context clip.
- Add a UI state showing prompt, evidence inputs, generated asset URL, and user approval.
- Store asset metadata in Postgres for auditability.

### Suggested Implementation Shape

Backend:

- Add `fal_api_key` to `Settings` in `backend/config.py`.
- Add `backend/tools/fal_client.py`.
- Add a new optional agent step such as `visual_brief` or a route such as `/api/companies/{id}/visual`.
- Use safe prompts built from already-approved research fields, not arbitrary raw user input.
- Store generated asset URLs and prompt metadata in a new table or a JSON column.

Frontend:

- Add a visual preview panel on the company detail or pipeline card.
- Show loading, generated, failed, and regenerated states.
- Make the media optional for the core Open Innovation demo unless the fal side challenge is targeted.

Guardrails:

- Do not send secrets or private profile data into media prompts.
- Avoid using real company logos unless the source and usage are acceptable.
- Keep the prompt evidence-based: role, stack, company domain, candidate project, and recent news.

## Tavily

### Manual Offer

The manual lists Tavily as:

- Real-time search, extraction, research, and web crawling through a single, secure API.

Hackathon access details in the manual:

- Sign up under Tavily.com to receive `1,000 free credits`.
- If credits run out, use code `TVLY-NK10WB6D` to generate more credits.
- Docs: https://docs.tavily.com/welcome

### Platform Capabilities

Tavily is the live-web evidence layer. In HuntAgent terms, it can:

- Search the current web for companies, jobs, funding, product pages, and news.
- Extract raw page content for downstream agents.
- Crawl or map a company site when a single page is not enough.
- Support deeper research workflows with cited sources.
- Reduce stale model knowledge by grounding the agent in current pages.

Tavily should be presented as the "web scout": it goes out first and brings back
evidence that other agents can inspect.

### Current Implementation

Relevant files:

- `backend/tools/tavily_client.py`
- `backend/agents/discovery.py`
- `backend/agents/research.py`
- `backend/tests/test_tavily_client.py`
- `backend/config.py`

Configuration:

- `TAVILY_API_KEY`

Current behavior:

- The client uses Tavily's synchronous SDK inside `asyncio.to_thread(...)`.
- Search depth is `advanced`.
- `include_raw_content=True` is enabled.
- Discovery searches profile-driven queries across job boards, ATS pages, and startup hiring signals.
- Research searches funding rounds, product/mission information, tech stack, recent news, and the specific job URL when available.
- URL-like queries are normalized and validated before Tavily receives them.

Security details:

- `file://` and other non-http schemes are rejected.
- Public HTTPS URL validation protects against unsafe outbound requests.
- Tests cover URL normalization and unsafe scheme rejection.

### Artistic Use In The Demo

Frame Tavily as "the scout that brings receipts."

Concrete demo beats:

- Show the generated search queries from the user's profile.
- Show a Tavily result becoming a candidate company.
- Show a job URL being re-searched by Tavily for raw job content.
- Show the raw search evidence feeding both Pioneer extraction and Gemini synthesis.

Best visible evidence:

- Activity feed: discovery found company via domain.
- Research logs: company enriched with funding stage, tech stack, recent news.
- UI detail view: source URL and job URL.

### Next Upgrade

The current code uses Tavily Search. To make the Tavily integration more
complete, consider using the broader Tavily surface:

- Extract: retrieve clean content from specific job and company URLs.
- Crawl: inspect a company's careers, about, blog, and engineering pages.
- Map: discover useful site URLs before crawling.
- Research: run deeper sourced research for high-fit companies.

Submission phrasing:

> Tavily is how the agent avoids stale knowledge. Every lead starts as a live
> web result, then HuntAgent filters, extracts, and reasons over current
> evidence before asking the user to approve outreach.

## Aikido

### Manual Offer

Aikido appears as a side challenge rather than in the main resource section.

Manual requirements:

- Create a free Aikido account.
- Connect the team's Git system to Aikido.
- Connect the repo being built during the hackathon.
- Take a screenshot of the security report, clearly showing the number and categories of issues.
- Prize: 1000 EUR for the most secure build.

Relevant manual/help links:

- Aikido: https://www.aikido.dev/
- Git connection help: https://help.aikido.dev/code-scanning/connect-your-source-code/connect-github-account-to-aikido

### Platform Capabilities

Aikido is the security critic. In HuntAgent terms, it can:

- Scan the repository for security issues before submission.
- Surface dependency, secret, code, container, and configuration risks depending on enabled scanners.
- Give judges a clear report with issue counts and categories.
- Help prove that the app is not just powerful but safe enough to operate with real outreach accounts and API keys.

### Current Implementation

Current status:

- No Aikido API integration exists in the app.
- `README.md` lists Aikido as a partner with the instruction to connect the repo for security scanning.
- The codebase already includes some relevant local security work:
  - `backend/tools/safe_http.py` centralizes outbound URL validation.
  - Tavily URL queries reject unsafe schemes.
  - Research sanitizes company websites and job URLs before using them in site filters or searches.
  - Pioneer outbound calls are restricted to `api.pioneer.ai`.
  - Human approval via Telegram prevents automatic delivery of generated messages.

### Artistic Use In The Demo

Frame Aikido as "the security critic in the agent room."

Concrete demo beats:

- Show the Aikido dashboard screenshot in the final submission.
- Point to local code protections around SSRF and unsafe URL handling.
- Explain that the product touches external web pages, messaging accounts, and API keys, so security is part of the workflow rather than an afterthought.

### Submission Checklist

Before submitting:

1. Create or log into the Aikido account.
2. Connect the Git provider.
3. Connect this repository.
4. Run the scan.
5. Fix high-signal issues if time allows.
6. Capture the report screenshot with visible issue counts and categories.
7. Include the screenshot in the project submission.

Recommended submission phrasing:

> HuntAgent is an agentic outreach system, so safety matters. We used Aikido to
> scan the repository and paired that with in-code outbound request validation
> and a mandatory human approval gate before messages are sent.

## Operational Event Resources

These are not AI platform resources, but they matter for execution:

| Resource | What it is for | Team use |
| --- | --- | --- |
| Discord server | Event communication | Ask resource-provider questions, resolve API/account access issues, and track announcements |
| Project submission form | Final submission | Include demo URL, repo, resource usage explanation, screenshots, and side-challenge proof |
| Venue address | On-site coordination | Use for team logistics and temporary account/resource help |
| Google temporary account help link | Gemini account setup | Use on site if personal keys fail or credits are not available |
| Pioneer onboarding link | Pioneer setup | Use to configure model id, API key, and side-challenge requirements |
| fal coupon link | fal credits | Claim before adding any media generation flow |
| Tavily docs link and credit code | Tavily setup | Activate credits and keep the research/discovery pipeline running |
| Aikido help link | Security setup | Connect the repo and capture the report screenshot |

## Recommended Demo Narrative

Use a short, vivid resource narrative:

1. Tavily scouts the live web and brings back current pages.
2. Pioneer reads raw job text through a structured entity lens.
3. Gemini acts as the strategist: filtering, synthesizing, scoring, selecting a contact, and writing.
4. fal, if implemented, turns the recommendation into a visual opportunity dossier.
5. Telegram keeps a human in control before delivery.
6. Aikido checks that the build is secure enough to trust.

This gives each resource a clear place in the story:

- Scout: Tavily
- Lens: Pioneer
- Strategist: Gemini
- Storyteller: fal
- Security critic: Aikido
- Human gate: Telegram

## Implementation Priority

### Already Strong

These are implemented and should be shown live:

- Tavily search and raw-content retrieval in discovery and research.
- Gemini relevance gating, research synthesis, scoring, contact selection, outreach drafting, and follow-up drafting.
- Pioneer/GLiNER2 schema extraction from job-posting text.
- Human approval gate through Telegram.
- Safe outbound URL handling for Tavily and research flows.

### Highest Impact Before Submission

1. Add resource badges or labels in the dashboard and activity feed.
   - Example: "Tavily found", "Pioneer extracted", "Gemini scored".
   - This makes resource use visible without changing core behavior.

2. Add an evidence trail for each company.
   - Store or display source URL, extracted entities, fit reasoning, and outreach hook.
   - Judges should see how the system moved from web evidence to human-approved action.

3. Run Aikido and capture the security report.
   - This is likely faster than building a deep integration.
   - It supports the Most Secure Build side challenge.

4. Decide whether fal is a core feature or a submission note.
   - For Open Innovation, a lightweight visual dossier is enough if it is stable.
   - For the fal side challenge, generative media must become a main feature.

5. If targeting the Fastino side challenge, fine-tune or evaluate Pioneer.
   - The current extraction path is real, but the side challenge rewards deeper use.

### Defer Unless Time Is Plentiful

- Fully automated media attachment in outreach.
- Real-time voice/video agents.
- Multi-step fal workflows with custom LoRA training.
- Autonomous sending without human approval.
- Broad crawling of every company website without rate limits and source controls.

## Environment Checklist

Existing active application settings:

- `GEMINI_API_KEY`
- `GEMINI_MODEL`
- `TAVILY_API_KEY`
- `PIONEER_API_KEY`
- `PIONEER_MODEL_ID`
- `UNIPILE_API_KEY`
- `UNIPILE_ACCOUNT_ID`
- `UNIPILE_DSN`
- `RESEND_API_KEY`
- `RESEND_FROM_EMAIL`
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`
- `DATABASE_URL`
- `SYNC_DATABASE_URL`

fal setting status:

- `.env.example` contains `FAL_API_KEY=`.
- `backend/config.py` does not yet include `fal_api_key`.
- No runtime code currently reads or uses `FAL_API_KEY`.

External/manual setup:

- Google temporary accounts may be supplied on site.
- Pioneer onboarding must be completed through the provided page.
- Tavily credits and additional code should be activated before the demo.
- fal voucher should be claimed before media generation.
- Aikido must be connected to the repo to produce a valid security screenshot.

## Submission Phrasing

Suggested concise explanation:

> HuntAgent is an Open Innovation project that uses the hackathon resources as
> a coordinated agent team. Tavily gathers current web evidence, Pioneer
> extracts structured job entities, Gemini filters and reasons over the
> evidence to score fit and draft outreach, fal can generate a visual opportunity
> dossier from the same evidence, and Aikido validates the repository security.
> The product keeps a human in the loop through Telegram before any message is
> sent.

Suggested side-challenge notes:

- Fastino/Pioneer: "We use Pioneer for schema-guided job entity extraction, and the next step is a fine-tuned/evaluated model that replaces a general-purpose LLM extraction call."
- fal: "fal is only a side-challenge candidate if the generated media artifact becomes a core feature, not a decoration."
- Aikido: "The repo should be connected and the report screenshot included as explicit proof."

## Source Links

Manual and event links:

- https://techeurope.notion.site/munich-hack
- https://discord.gg/brSqTjJVdh
- https://tally.so/r/XxNqDd

Resource links:

- https://deepmind.google/
- https://goo.gle/hackathon-account
- https://ai.google.dev/gemini-api/docs
- https://pioneer.ai/
- https://fastino.ai/
- https://docs.pioneer.ai/
- https://wholesale-mackerel-22f.notion.site/Munich-Hackathon-Onboarding-3798413d4744807e8dcdc50f1cbc8419?source=copy_link
- https://fal.ai/
- https://fal.ai/docs
- http://fal.ai/coupon-claim/techeurope-munich
- https://www.tavily.com/
- https://docs.tavily.com/welcome
- https://www.aikido.dev/
- https://help.aikido.dev/code-scanning/connect-your-source-code/connect-github-account-to-aikido
