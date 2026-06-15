# M002-qqpa83: Pioneer Evaluation and Model Quality

**Vision:** Build a measured evaluation pipeline comparing Pioneer/GLiNER2 vs Gemini entity extraction on synthetic data, with conditional fine-tuning and a visual comparison chart in the company dossier — targeting the Fastino side challenge.

## Success Criteria

- 30-50 synthetic Tech/Startups job postings generated via Gemini Structured Outputs and stored locally as JSON
- Token-overlap F1 scores computed per label comparing Pioneer vs Gemini extraction
- Conditional fine-tuning triggered when mean F1 < 80%, with graceful degradation on failure
- Visual Recharts comparison chart renders successfully in Next.js company dossier for pioneer-eval evidence events
- Pytest suite passes covering F1 calculation, fine-tuning trigger logic, and integration fixtures

## Slices

- [ ] **S01: Synthetic Data Generation and F1 Evaluation Engine** `risk:medium` `depends:[]`
  > After this: After this, running the generator script produces 30-50 synthetic job postings as JSON, and the evaluator computes per-label F1 scores comparing Pioneer vs Gemini extraction. Pytest proves F1 calculation correctness with static fixtures.

- [ ] **S02: Pioneer Training Integration and Conditional Fine-Tuning** `risk:high` `depends:[S01]`
  > After this: After this, the evaluator conditionally triggers Pioneer fine-tuning when mean F1 < 80%. If the training API is unavailable, the pipeline logs the failure and continues with base model results. Pytest proves the conditional logic and graceful degradation.

- [ ] **S03: Evaluation Persistence and Visual Comparison Chart** `risk:low` `depends:[S01,S02]`
  > After this: After this, evaluation results are saved as pioneer-eval evidence events in PostgreSQL. The Next.js company dossier renders a Recharts BarChart showing per-label F1 scores for Pioneer vs Gemini. npm run typecheck and npm run lint pass.

## Boundary Map

Not provided.
