# Codebase Map

Generated: 2026-06-15T16:14:50Z | Files: 99 | Described: 0/99
<!-- gsd:codebase-meta {"generatedAt":"2026-06-15T16:14:50Z","fingerprint":"289620b5c6b30ea061cbe209e2550d6f35f9bbca","fileCount":99,"truncated":false} -->

### (root)/
- `.aikido.yml`
- `.env.example`
- `.gitignore`
- `ARCHITECTURE.md`
- `docker-compose.yml`
- `pyproject.toml`
- `README.md`
- `SECURITY.md`

### .github/
- `.github/dependabot.yml`
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

### backend/eval/
- `backend/eval/__init__.py`
- `backend/eval/evaluator.py`
- `backend/eval/finetune.py`
- `backend/eval/generator.py`
- `backend/eval/metrics.py`
- `backend/eval/persist.py`

### backend/schemas/
- `backend/schemas/dossier.py`
- `backend/schemas/evidence.py`

### backend/scripts/
- `backend/scripts/seed_demo_dossier.py`

### backend/tests/
- `backend/tests/conftest.py`
- `backend/tests/test_dossier.py`
- `backend/tests/test_eval_evaluator.py`
- `backend/tests/test_eval_finetune.py`
- `backend/tests/test_eval_metrics.py`
- `backend/tests/test_evidence.py`
- `backend/tests/test_fal_client.py`
- `backend/tests/test_fal.py`
- `backend/tests/test_safe_http.py`
- `backend/tests/test_tavily_client.py`

### backend/tests/fixtures/
- `backend/tests/fixtures/eval_synthetic_sample.json`
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

### frontend/dummy-sharp/
- `frontend/dummy-sharp/index.js`
- `frontend/dummy-sharp/package.json`

### frontend/lib/
- `frontend/lib/api.ts`

### frontend/public/
- `frontend/public/signal.json`
