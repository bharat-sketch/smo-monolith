# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Wynisco SMO (Student Marketing Operations) — a recruiting/talent management platform. Two services share a PostgreSQL database, deployed together in a single Cloud Run container for the test environment, and separately on Google App Engine for production.

This is a **git monolith with submodules**:
- `be-fastapi-smo/` → `Wynisco-Engineering/be-fastapi-smo`
- `fe-react-smo/` → `Wynisco-Engineering/fe-react-smo`
- `auto-matching-service/` → `bharat-sketch/auto-matching-service` (legacy — matching is now integrated into be-fastapi-smo under `app/matching/`)

**Always push the submodule first, then the monolith.** Pushing the monolith to `main` triggers CI/CD deployment.

## Commands

### be-fastapi-smo (port 8000)

```bash
cd be-fastapi-smo
pip install -r requirements.txt
alembic upgrade head                              # run migrations
alembic revision --autogenerate -m "description"  # create migration
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
TEST_BASE_URL=http://localhost:8000 TEST_EMAIL=you@wynisco.com TEST_PASSWORD=pass pytest tests/ -v
pytest tests/test_health.py -v                    # single test file
```

### fe-react-smo (port 3000)

```bash
cd fe-react-smo
npm install
npm run start           # dev server
npm run build           # production build
npm run test:e2e        # Playwright E2E tests (e2e/ directory)
```

### auto-matching-service/frontend (port 3001)

```bash
cd auto-matching-service/frontend
npm install
npm run dev             # Next.js dev — proxies /api/* to localhost:8002
npm run lint
```

### CI/CD Deployment

```bash
# Automatic: push to main triggers GitHub Actions → Cloud Run
git push origin main

# Manual:
gcloud builds submit --tag asia-south1-docker.pkg.dev/student-marketing-operations/smo-test/smo-test:latest
gcloud run deploy smo-test --image asia-south1-docker.pkg.dev/student-marketing-operations/smo-test/smo-test:latest --region asia-south1
```

## Architecture

### Cloud Run Container (Test Environment)

Single container runs two processes via `start.py`:
- **nginx** (:8080) — serves React static files, proxies `/api/*` to uvicorn
- **uvicorn SMO** (:8000) — FastAPI backend with 34 routers (matching integrated)

No CORS needed — frontend and backend share the same origin via nginx.

Request flow for AI matching: `Frontend → nginx → SMO /api/v1/matching/*` (direct, no proxy)

### be-fastapi-smo — Layered Pattern

All routes mounted at `/api/v1/{resource}` in `app/main.py`. Layered:

- **`app/api/v1/`** — Route handlers (one file per resource, 34 routers)
- **`app/api/deps.py`** — Auth dependencies (see below)
- **`app/crud/`** — Database query logic
- **`app/models/`** — SQLAlchemy 2.0 async ORM models
- **`app/schemas/`** — Pydantic v2 request/response schemas
- **`app/core/`** — Config (`config.py`), async DB engine (`database.py`), JWT auth (`auth_utils.py`), rate limiter (`limiter.py`)
- **`app/utils/`** — Integrations (Google Drive, GCS, Apify, OpenAI, Mailgun)
- **`app/matching/`** — AI matching engine (formerly auto-matching-service)
  - `services/matching_engine.py` — Orchestrator: Hard Filter → Semantic ANN → LLM Score
  - `services/embedding_service.py` — OpenAI text-embedding-3-large embeddings
  - `services/llm_scorer.py` — Cerebras gpt-oss-120b LLM scoring
  - `services/cerebras_client.py` — Cerebras API client
  - `services/semantic_scorer.py` — pgvector cosine similarity
  - `services/hard_filter.py` — SQL-based candidate/job elimination
  - `services/why_card.py` — Score breakdown builder
  - `redis_client.py` — Async Redis cache with graceful fallback

**Auth dependencies** (`app/api/deps.py`):
- `get_current_user` — base auth, blocks alumni role
- `get_current_admin_user` — requires `privilege` in `["admin", "superadmin"]`
- `get_current_superadmin_user` — requires `superadmin` privilege only
- `get_current_consultant_user` — requires consultant role or admin privilege
- `get_current_client_user` — requires client role or superadmin privilege
- `get_current_user_optional` — returns `None` if no token (for optional auth)

Note: `role` (candidate, consultant, instructor, alumni, client, counsellor, archive) is separate from `privilege` (user, admin, superadmin).

**Database session pattern** (`app/core/database.py`):
```python
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
```
Pool: `pool_size=8`, `max_overflow=4`, `pool_recycle=1800`, `pool_pre_ping=True`.

**Matching routes** (`app/api/v1/matching.py`): Direct route handlers for `/api/v1/matching/*` — match, dismiss, embeddings backfill, and candidate/job listing. All authenticated users can access matching; embeddings backfill requires admin.

### fe-react-smo

React 18 CRA app (react-scripts). **JavaScript, no TypeScript.**

- `src/pages/` — Route pages including `AIMatching/`
- `src/services/` — API client modules (`api.js` base + per-resource services including `MatchingService.js`)
- `src/components/` — Reusable UI components (Sidebar, Header, ProtectedRoute, ClientProtectedRoute)
- `src/context/` — React context providers (UserContext for role-based rendering)

### Matching Engine (app/matching/) — 2-Layer Pipeline

Integrated into be-fastapi-smo (formerly standalone auto-matching-service).

1. **Hard Filter** — SQL-based elimination (employer blocklist, job recency, experience)
2. **Semantic** — pgvector cosine similarity on OpenAI `text-embedding-3-large` vectors
3. **LLM** — Cerebras `gpt-oss-120b` scoring with structured prompts

Key services under `be-fastapi-smo/app/matching/services/`: `matching_engine.py`, `embedding_service.py`, `semantic_scorer.py`, `llm_scorer.py`, `cerebras_client.py`, `hard_filter.py`, `why_card.py`

Uses the same SMO models directly (no readonly copies). Redis caching for LLM results with graceful fallback.

## Conventions

- Python: snake_case functions/variables, PascalCase classes, type hints required
- Imports grouped: stdlib, third-party, local
- Config via Pydantic Settings in each service's `app/core/config.py`, loaded from `.env`
- All database access is async (asyncpg + SQLAlchemy async sessions)
- API pagination: `page`, `size` params → response with `total`, `total_pages`
- Auth: JWT Bearer tokens with role-based access control
- fe-react-smo: JavaScript (ES6+), functional components + hooks, Tailwind CSS, API calls in `src/services/`

## Technical Gotchas

- pgvector returns numpy float32 — always convert with `[float(x) for x in vec]`
- asyncpg doesn't support `::vector` cast — use `CAST(:param AS vector)` instead
- OpenAI batch embedding limit ~300K tokens — `EMBEDDING_BATCH_SIZE=256` works safely
- Cloud Run requires `--no-cpu-throttling` — Python imports take 30s+ with throttled CPU on cold start
- Submodule URLs in `.gitmodules` must be HTTPS (not SSH) for CI/CD token auth to work
- Client role is restricted to `/api/v1/auth/` and `/api/v1/talent-hub/` endpoints only (enforced in middleware)

## Environment Variables

**be-fastapi-smo**: `DATABASE_URL` (required, `postgresql+asyncpg://...`), `OPENAI_API_KEY`, `APIFY_API_TOKEN`, `MAILGUN_API_KEY`, `MAILGUN_DOMAIN`, `GOOGLE_DRIVE_CREDENTIALS_JSON`, `SHARED_DRIVE_ID`, `ENABLE_SEMANTIC_SEARCH`, `FRONTEND_URL`, `CEREBRAS_API_KEY` (for matching LLM scoring), `REDIS_URL` (optional, matching LLM cache)

## Deployment

- **Production**: App Engine — `gcloud app deploy` in each service directory
- **Test**: Cloud Run — push to `main` triggers CI/CD (`.github/workflows/deploy-cloud-run.yml`)
- **Test URL**: `https://smo-test-seek2wfd4q-el.a.run.app`
- **GCP project**: `student-marketing-operations`
- **Database**: Cloud SQL instance `student-marketing-operations:asia-south1:smo`, databases `smo` (prod) and `smo_test` (test)
- **Secrets**: GCP Secret Manager (`smo-openai-api-key`, `smo-cerebras-api-key`, `smo-apify-api-token`, `smo-gdrive-service-account`)
- **Mailgun intentionally omitted** from test env to prevent sending real emails
