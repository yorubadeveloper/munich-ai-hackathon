# S04: Repo Hardening and Submission Docs

**Goal:** Add SECURITY.md, Dependabot config, dependency-review actions, fix README version drift, write the final submission narrative, and ensure frontend lint/typechecks pass.
**Demo:** Repository contains required security and dependency configs, and documentation clearly outlines the submission narrative.

## Must-Haves

- SECURITY.md and dependabot.yml exist
- README contains submission narrative
- Frontend passes linting and typechecks

## Proof Level

- This slice proves: manual

## Integration Closure

S04 wraps up the repo hygiene and documentation required for final submission.

## Verification

- CI provides visibility into dependency vulnerabilities and frontend build passing.

## Tasks

- [x] **T01: Verified Security and Dependabot Setup** `est:30m`
  Create `SECURITY.md`, `.github/dependabot.yml`, and `.github/workflows/dependency-review.yml` for basic repository hygiene.
  - Files: `SECURITY.md`, `.github/dependabot.yml`, `.github/workflows/dependency-review.yml`
  - Verify: Verify file existence and YAML validity.

- [x] **T02: Prepared Submission Narrative Docs** `est:1h`
  Update the `README.md` to fix version drift and write the full hackathon submission narrative.
  - Files: `README.md`
  - Verify: Verify README renders correctly.

## Files Likely Touched

- SECURITY.md
- .github/dependabot.yml
- .github/workflows/dependency-review.yml
- README.md
