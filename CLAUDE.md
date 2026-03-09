# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Wynisco — a recruiting/talent management platform with four independent services sharing a PostgreSQL database (`smo_local`):

1. **be-fastapi-smo/** — Core SMO (Student Marketing Operations) backend. Manages jobs, candidates, applications, interviews, pods (cohorts), employers, attendance tracking, and more. Deployed on Google App Engine.
2. **fe-react-smo/** — React 18 + Tailwind CSS frontend for SMO. Uses react-router-dom, Axios, context-based state management. Deployed on Google App Engine.
3. **matching-service/** — AI-powered candidate-job matching engine with analytics dashboard. Backend uses Cerebras LLM for scoring; frontend is Next.js 16 + React 19. Deployed on Railway.
4. **auto-matching-service/** — Automated 3-layer matching engine (semantic embeddings + rule scoring + LLM scoring) with Redis caching. Has its own Next.js 16 frontend. Separate git repo.

Each service directory is its own git repository. The parent directory is **not** a git repo.

## Commands

### be-fastapi-smo (port 8000)

```bash
cd be-fastapi-smo
pip install -r requirements.txt
alembic upgrade head                              # run migrations
alembic revision --autogenerate -m "description"  # create migration
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
flake8                                            # lint
mypy app                                          # type check
pytest app/tests/                                 # tests (currently empty)
gcloud app deploy                                 # deploy
```

### fe-react-smo (port 3000)

```bash
cd fe-react-smo
npm install
npm run start           # dev server
npm run build           # production build
npm run test:e2e        # Playwright E2E tests (e2e/ directory)
gcloud app deploy       # deploy (run npm run build first)
```

### matching-service/backend (port 8001)

```bash
cd matching-service/backend
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
# Deploy: railway up backend/ --path-as-root --service resume-matcher
```

### matching-service/frontend (port 3000)

```bash
cd matching-service/frontend
npm install
NEXT_PUBLIC_API_URL=http://localhost:8001 npm run dev
# Deploy: railway up frontend/ --path-as-root --service frontend
```

### auto-matching-service (port 8002)

```bash
cd auto-matching-service
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --host 0.0.0.0 --port 8002
```

Uses a separate Alembic version table (`alembic_version_auto_matcher`) to avoid conflicts with SMO migrations.

### auto-matching-service/frontend (port 3001)

```bash
cd auto-matching-service/frontend
npm install
npm run dev             # Next.js dev on port 3001
npm run lint            # ESLint
```

Next.js proxy: `next.config.ts` rewrites `/api/*` to `localhost:8002/api/*`, so the frontend API client uses relative URLs.

## Architecture

### be-fastapi-smo

FastAPI app with 34 routers, all mounted at `/api/v1/`. Layered pattern:

- **`app/api/v1/`** — Route handlers (one file per resource)
- **`app/crud/`** — Database query logic
- **`app/models/`** — SQLAlchemy 2.0 async ORM models (32 models)
- **`app/schemas/`** — Pydantic v2 request/response schemas
- **`app/core/`** — Config (`config.py` via Pydantic Settings), async DB engine (`database.py`), JWT auth (`auth_utils.py`), rate limiter (`limiter.py`)
- **`app/credentials/`** — Auth/authorization utilities
- **`app/utils/`** — Integrations (Google Drive, GCS, Apify scraping, OpenAI, Mailgun, BigQuery)
- **`alembic/`** — 44+ migration files

Key middleware in `main.py`: request logging with user context extraction, client role access blocking (clients restricted to `/api/v1/auth/` and `/api/v1/talent-hub/`), rate limiting via SlowAPI.

User roles: candidate, instructor, consultant, alumni, admin, client.

### fe-react-smo

React 18 CRA app (react-scripts). JavaScript, no TypeScript.

- **`src/pages/`** — Route pages (jobs, pods, Employers, Interviews, Dashboard, etc.)
- **`src/services/`** — API service modules (api.js base + per-resource services)
- **`src/components/`** — Reusable UI components
- **`src/context/`** — React context providers for shared state

### matching-service/backend

Smaller FastAPI app with 4 routers: candidates, jobs, matching, analytics. Uses read-only mapped classes for shared SMO database tables and a `match_results` cache table (24-hour TTL).

Matching pipeline: filter → structured pre-scoring (skills, experience, location, salary, visa) → LLM scoring via Cerebras (`gpt-oss-120b`) with async concurrency limits → cached results.

### matching-service/frontend

Next.js 16 + React 19 + TypeScript. Uses shadcn/ui, Tailwind CSS, Recharts, React Query.

### auto-matching-service

FastAPI app with 3 routers: matching, embeddings, listing. 3-layer scoring engine:

- **`app/services/embedding_service.py`** — OpenAI text-embedding-3-small, stored via pgvector
- **`app/services/semantic_scorer.py`** — Cosine similarity on embeddings
- **`app/services/rule_scorer.py`** — Structured pre-scoring (skills, experience, etc.)
- **`app/services/llm_scorer.py`** — Cerebras LLM scoring with async concurrency
- **`app/services/matching_engine.py`** — Orchestrates the 3-layer pipeline
- **`app/models/readonly.py`** — Read-only mapped classes for shared SMO tables
- **`app/core/redis_client.py`** — Optional Redis cache (falls back to DB-only)
- **`scripts/`** — Job description scraping and re-embedding utilities

### auto-matching-service/frontend

Next.js 16 + React 19 + TypeScript. Uses shadcn/ui, Tailwind v4, Recharts, React Query. Auth: sessionStorage key `auto_matcher_auth`.

## Conventions

- Python: snake_case functions/variables, PascalCase classes, type hints required
- Imports grouped: stdlib, third-party, local
- Config via environment variables loaded through Pydantic Settings in each service's `app/core/config.py`
- All database access is async (asyncpg + SQLAlchemy async sessions)
- API pagination pattern: `page`, `size` params → response with `total`, `total_pages`
- Auth: JWT Bearer tokens with role-based access control
- fe-react-smo: JavaScript (ES6+), functional components + hooks, Tailwind CSS utilities, API calls centralized in `src/services/`

## Technical Gotchas

- pgvector returns numpy float32 — always convert with `[float(x) for x in vec]`
- asyncpg doesn't support `::vector` cast — use `CAST(:param AS vector)` instead
- OpenAI batch embedding limit ~300K tokens — `EMBEDDING_BATCH_SIZE=256` works safely

## Environment Variables

**be-fastapi-smo**: `DATABASE_URL` (postgresql+asyncpg://...), plus optional `OPENAI_API_KEY`, `GOOGLE_APPLICATION_CREDENTIALS`, `APIFY_API_TOKEN`

**fe-react-smo**: `.env` with API endpoint configuration

**matching-service/backend**: `DATABASE_URL`, `CEREBRAS_API_KEY`, `FRONTEND_URL`

**matching-service/frontend**: `NEXT_PUBLIC_API_URL`

**auto-matching-service**: `DATABASE_URL`, `OPENAI_API_KEY`, `CEREBRAS_API_KEY`, optional `REDIS_URL` (falls back to DB-only cache). Tunable: `EMBEDDING_MODEL`, `EMBEDDING_DIMENSIONS`, `EMBEDDING_BATCH_SIZE`, `CEREBRAS_MODEL`, `LLM_CONCURRENCY_LIMIT`, `DEFAULT_TOP_N`, `SEMANTIC_TOP_K`, `LLM_TOP_N`, `MATCH_CACHE_TTL_HOURS`, `LLM_CACHE_TTL_HOURS`, `JOB_RECENCY_DAYS`, `WEIGHT_SEMANTIC`, `WEIGHT_LLM`
