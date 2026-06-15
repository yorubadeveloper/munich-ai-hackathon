# M003-n9ygqi: Creative Media and Submission Polish

**Vision:** Turn fal from an optional visual layer into a core generative media feature: visual opportunity dossier cards generated from the evidence trail and displayed in the dashboard. Add lightweight repo hardening and package the full hackathon resource narrative for submission.

## Success Criteria

- fal generates a visual opportunity card automatically after company evidence exists.
- Dossier renders the card or gracefully degrades if fal is missing.
- Repo hardening and submission narrative are fully completed.

## Slices

- [ ] **S01: fal Visual Card Client and Tests** `risk:medium` `depends:[]`
  > After this: Mocked fal client tests pass, validating circuit breaking and basic API interaction.

- [ ] **S02: Backend Pipeline fal Integration** `risk:medium` `depends:[S01]`
  > After this: Running the pipeline generates and saves a fal visual card evidence event to the database.

- [ ] **S03: Dashboard Dossier Visual Card UI** `risk:low` `depends:[S02]`
  > After this: Dashboard shows the generated visual card in the company dossier, or gracefully degrades when unavailable.

- [ ] **S04: Repo Hardening and Submission Docs** `risk:low` `depends:[]`
  > After this: Repository contains required security and dependency configs, and documentation clearly outlines the submission narrative.

## Boundary Map

- **fal.ai Client:** `backend/tools/fal_client.py` and `backend/tests/test_fal_client.py`
- **Orchestration/Integration:** Updates to the pipeline orchestrator to call the fal client post-research.
- **Frontend Dossier UI:** `frontend/components/OptionalVisualDossier.tsx` or similar component in the Next.js app.
- **Docs & CI:** `SECURITY.md`, `.github/dependabot.yml`, `README.md`, `frontend/package.json`
