---
estimated_steps: 13
estimated_files: 2
skills_used: []
---

# T02: Build PioneerEvalChart Recharts component and integrate into dossier

Create `frontend/components/PioneerEvalChart.tsx`:

1. Accept `events: EvidenceEvent[]` as props (same pattern as ResourceChartInner).
2. Filter events for `artifact_type === 'pioneer-eval'` and `status === 'success'`.
3. If no matching event, render nothing (return null).
4. Extract `per_label_f1_pioneer` and `per_label_f1_gemini` from the payload.
5. Transform into Recharts data format: `[{label: 'company_name', Pioneer: 0.85, Gemini: 0.92}, ...]`.
6. Render a `BarChart` with grouped bars (Pioneer blue, Gemini orange) per entity label.
7. Include chart title, legend, axis labels.
8. Use `ResponsiveContainer` for responsive sizing.

Integrate into the company dossier page:
1. Import PioneerEvalChart in `frontend/app/companies/[id]/page.tsx`.
2. Add it below the existing ResourceChart section with an appropriate heading.
3. Pass the same `dossier.evidence_events` array.

## Inputs

- `frontend/components/ResourceChartInner.tsx`
- `frontend/lib/api.ts`

## Expected Output

- `frontend/components/PioneerEvalChart.tsx`

## Verification

cd frontend && npm run typecheck && npm run lint
