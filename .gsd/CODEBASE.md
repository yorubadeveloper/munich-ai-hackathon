# Codebase Map

Generated: 2026-06-13T19:41:19Z | Files: 62 | Described: 0/62
<!-- gsd:codebase-meta {"generatedAt":"2026-06-13T19:41:19Z","fingerprint":"9625fd325caa6c23a8085e85690acbeb8a777243","fileCount":62,"truncated":false} -->

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
- `.github/workflows/docker-build.yml`

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
- `backend/api/log.py`
- `backend/api/profile.py`
- `backend/api/run.py`

### backend/tests/
- `backend/tests/test_safe_http.py`
- `backend/tests/test_tavily_client.py`

### backend/tg/
- `backend/tg/__init__.py`
- `backend/tg/bot.py`

### backend/tools/
- `backend/tools/__init__.py`
- `backend/tools/gemini_client.py`
- `backend/tools/gliner_client.py`
- `backend/tools/safe_http.py`
- `backend/tools/tavily_client.py`
- `backend/tools/telegram_client.py`
- `backend/tools/unipile_client.py`

### frontend/
- `frontend/.dockerignore`
- `frontend/Dockerfile`
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

### frontend/app/dashboard/
- `frontend/app/dashboard/page.tsx`

### frontend/app/setup/
- `frontend/app/setup/page.tsx`

### frontend/components/
- `frontend/components/ActivityFeed.tsx`
- `frontend/components/AddCompany.tsx`
- `frontend/components/CompanyCard.tsx`
- `frontend/components/Lottie.tsx`
- `frontend/components/PipelineBoard.tsx`
- `frontend/components/StatBar.tsx`
- `frontend/components/StatusBadge.tsx`

### frontend/lib/
- `frontend/lib/api.ts`

### frontend/public/
- `frontend/public/signal.json`
