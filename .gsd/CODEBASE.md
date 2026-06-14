# Codebase Map

Generated: 2026-06-14T23:36:21Z | Files: 84 | Described: 0/84
<!-- gsd:codebase-meta {"generatedAt":"2026-06-14T23:36:21Z","fingerprint":"1332f5eba9cbae39961e222e95ecb8825d7afe5f","fileCount":84,"truncated":false} -->

### (root)/
- `.env.example`
- `.gitignore`
- `ARCHITECTURE.md`
- `docker-compose.yml`
- `pyproject.toml`
- `README.md`

### .github/
- `.github/PULL_REQUEST_TEMPLATE.md`

### .github/workflows/
- `.github/workflows/ci-lint.yml`
- `.github/workflows/ci-tests.yml`
- `.github/workflows/docker-build.yml`
- `.github/workflows/jules_automerge.yml`
- `.github/workflows/jules_next_task.yml`

### backend/
- `backend/.dockerignore`
- `backend/.python-version`
- `backend/config.py`
- `backend/database.py`
- `backend/Dockerfile`
- `backend/main.py`
- `backend/models.py`
- `backend/pyproject.toml`
- `backend/requirements.txt`

### backend/agents/
- `backend/agents/__init__.py`
- `backend/agents/delivery.py`
- `backend/agents/discovery.py`
- `backend/agents/followup.py`
- `backend/agents/orchestrator.py`
- `backend/agents/outreach.py`
- `backend/agents/research.py`

### backend/api/
- `backend/api/__init__.py`
- `backend/api/companies.py`
- `backend/api/dossier.py`
- `backend/api/log.py`
- `backend/api/profile.py`
- `backend/api/run.py`

### backend/schemas/
- `backend/schemas/dossier.py`
- `backend/schemas/evidence.py`

### backend/scripts/
- `backend/scripts/seed_demo_dossier.py`

### backend/tests/
- `backend/tests/conftest.py`
- `backend/tests/test_dossier.py`
- `backend/tests/test_evidence.py`
- `backend/tests/test_fal_client.py`
- `backend/tests/test_fal.py`
- `backend/tests/test_safe_http.py`
- `backend/tests/test_tavily_client.py`

### backend/tests/fixtures/
- `backend/tests/fixtures/evidence.py`

### backend/tg/
- `backend/tg/__init__.py`
- `backend/tg/bot.py`

### backend/tools/
- `backend/tools/__init__.py`
- `backend/tools/fal_client.py`
- `backend/tools/gemini_client.py`
- `backend/tools/gliner_client.py`
- `backend/tools/safe_http.py`
- `backend/tools/tavily_client.py`
- `backend/tools/telegram_client.py`
- `backend/tools/unipile_client.py`

### docs/
- `docs/hackathon-resource-map.md`

### frontend/
- `frontend/.dockerignore`
- `frontend/Dockerfile`
- `frontend/eslint.config.mjs`
- `frontend/next-env.d.ts`
- `frontend/next.config.js`
- `frontend/package-lock.json`
- `frontend/package.json`
- `frontend/tsconfig.json`
- `frontend/tsconfig.tsbuildinfo`

### frontend/app/
- `frontend/app/globals.css`
- `frontend/app/layout.tsx`
- `frontend/app/page.tsx`

### frontend/app/companies/[id]/
- `frontend/app/companies/[id]/page.tsx`

### frontend/app/dashboard/
- `frontend/app/dashboard/page.tsx`

### frontend/app/setup/
- `frontend/app/setup/page.tsx`

### frontend/components/
- `frontend/components/ActivityFeed.tsx`
- `frontend/components/AddCompany.tsx`
- `frontend/components/ApprovalActions.tsx`
- `frontend/components/CompanyCard.tsx`
- `frontend/components/Lottie.tsx`
- `frontend/components/OptionalVisualDossier.tsx`
- `frontend/components/PipelineBoard.tsx`
- `frontend/components/ResourceChart.tsx`
- `frontend/components/ResourceChartInner.tsx`
- `frontend/components/StatBar.tsx`
- `frontend/components/StatusBadge.tsx`

### frontend/lib/
- `frontend/lib/api.ts`

### frontend/public/
- `frontend/public/signal.json`
