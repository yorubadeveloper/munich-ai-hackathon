# Decisions Register

<!-- Append-only. Never edit or remove existing rows.
     To reverse a decision, add a new row that supersedes it.
     Read this file at the start of any planning or research phase. -->

| # | When | Scope | Decision | Choice | Rationale | Revisable? | Made By |
|---|------|-------|----------|--------|-----------|------------|---------|
| D001 | 2026-06-14 | M002-qqpa83 | What charting library to use for the visual comparison chart in the Next.js dossier UI. | Recharts | Recharts provides simple, declarative React components that look great out of the box and natively support radar/bar charts perfect for comparing multiple labels. | Yes | collaborative |
| D002 | 2026-06-14 | M002-qqpa83 | How to handle fine-tuning failures if the Pioneer training API is inaccessible. | Graceful Degradation | Prevents a fragile external dependency (training API during a hackathon) from blocking the core evaluation pipeline and evidence display. The pipeline will log the error and continue using the base model's evaluation results. | Yes | collaborative |
| D003 |  | M002-qqpa83 | What charting library to use for the visual comparison chart in the Next.js dossier UI. | Recharts | Recharts provides simple, declarative React components that look great out of the box and natively support radar/bar charts perfect for comparing multiple labels. | Yes | collaborative |
| D004 |  | M002-qqpa83 | How to handle fine-tuning failures if the Pioneer training API is inaccessible. | Graceful Degradation | Prevents a fragile external dependency (training API during a hackathon) from blocking the core evaluation pipeline and evidence display. The pipeline will log the error and continue using the base model's evaluation results. | Yes | collaborative |
| D005 | M001-8itnlq/S04 | M001-8itnlq/S04 | How to integrate fal.ai visual generation into the company research pipeline | Fire-and-forget after research.run() with circuit-breaking (empty key check, try/except, 30s timeout), storing results as EvidenceEvents | fal must be strictly non-blocking per the hackathon constraint. Injecting after research completes means the pipeline never waits on fal, and storing results as EvidenceEvents keeps it consistent with the S01/S02 evidence trail contract. Missing credentials produce error events rather than crashes. | Yes | agent |
