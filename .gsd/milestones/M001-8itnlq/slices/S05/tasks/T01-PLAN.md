---
estimated_steps: 8
estimated_files: 1
skills_used: []
---

# T01: Extended dossier API tests with Fal visual and partial-failure assertions, validating both the presence of visual evidence and robust handling of error-only evidence.

**Why:** The existing `test_dossier.py` includes `partial_failure_evidence` and several resource types but omits the `fal_evidence` fixture. The test does not explicitly assert that fal visual artifacts appear in the dossier response or that dossiers containing only error events are handled correctly. This task closes the test gap.

**Do:**
1. Add `fal_evidence` to the `test_get_dossier_success` fixture parameter list and include it in the `mock_events` loop.
2. Add an assertion that the response `evidence_events` list contains an event with `resource_name='fal'` and `artifact_type='visual_artifact'`.
3. Add a new test `test_get_dossier_partial_failures_only` that creates a dossier where the only evidence events have `status='error'`. Assert the dossier endpoint still returns 200 with an empty or degraded evidence list and no crash.
4. Verify the `fal_evidence` fixture in `backend/tests/fixtures/evidence.py` already has the correct shape (it does — `ResourceName.FAL`, `ArtifactType.VISUAL_ARTIFACT`, status success).
5. Run `uv run pytest backend/tests/test_dossier.py -v` to confirm all tests pass.

**Done-when:** All dossier tests pass, including assertions for fal visual evidence presence and a partial-failure-only scenario.

## Inputs

- `backend/tests/fixtures/evidence.py`
- `backend/schemas/evidence.py`
- `backend/schemas/dossier.py`
- `backend/api/dossier.py`
- `backend/models.py`

## Expected Output

- `backend/tests/test_dossier.py`

## Verification

cd backend && uv run pytest tests/test_dossier.py -v
