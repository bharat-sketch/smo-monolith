# Wynisco SMO Monolith

Wynisco's Student Marketing Operations (SMO) platform — a recruiting and talent management system with AI-powered candidate-job matching. This monolith repo ties together three independent services via git submodules, plus shared infrastructure for a combined Cloud Run test environment.

## Architecture

```
smo-monolith/
├── be-fastapi-smo/            # Backend API (FastAPI, Python 3.11)
├── fe-react-smo/              # Frontend (React 18, Tailwind CSS)
├── auto-matching-service/     # AI Matching Engine (FastAPI + Next.js)
├── Dockerfile                 # Combined container for Cloud Run
├── nginx.conf                 # Reverse proxy config
└── start.py                   # Container startup script
```

**Production** runs on Google App Engine (backend + frontend as separate services) with Cloud SQL (PostgreSQL).

**Test environment** runs as a single Cloud Run container with nginx reverse-proxying to uvicorn — no CORS needed, one URL, scale-to-zero.

```
┌─────────────────────────────────────────────────┐
│              Cloud Run Container                 │
│                                                  │
│   ┌─────────┐        ┌──────────────────┐       │
│   │  nginx   │──/api/→│    uvicorn       │       │
│   │  :8080   │        │    :8000         │       │
│   │          │        │  (FastAPI app)   │       │
│   │ static   │        │                  │       │
│   │ files    │        │    Cloud SQL     │       │
│   │ (React)  │        │    (smo_test)    │       │
│   └─────────┘        └──────────────────┘       │
└─────────────────────────────────────────────────┘
```

---

## Services

### be-fastapi-smo — Core Backend

FastAPI application with 34 API routers mounted at `/api/v1/`. Handles all business logic for the platform.

**Key features:**
- Job management, candidate tracking, applications, interviews
- Pod (cohort) management for training groups
- Employer and contact relationship management
- WynTrack — time tracking with punch-in/out and leave management
- QC dashboard with metrics analysis
- Talent Hub — public-facing candidate profiles for clients
- Digital Spaces — content management
- Resume parsing and semantic search (OpenAI embeddings + pgvector)
- Google Drive integration for document management
- Apify integration for job scraping
- Mailgun for transactional emails

**Tech stack:** FastAPI, SQLAlchemy 2.0 (async), asyncpg, Pydantic v2, Alembic, SlowAPI, passlib/bcrypt

**User roles:** `candidate`, `consultant`, `instructor`, `alumni`, `client`, `counsellor`, `archive`

**Privilege levels:** `user`, `admin`, `superadmin`

**Auth:** JWT Bearer tokens with role-based access control. Client role restricted to `/api/v1/auth/` and `/api/v1/talent-hub/` endpoints only.

### fe-react-smo — Frontend

React 18 single-page application with Tailwind CSS.

**Key pages:**
- Dashboard with role-based views
- Jobs board (all jobs, my jobs, job details)
- Candidates pipeline and profiles
- Employer and contact management
- Interview scheduling and tracking
- Activity tracking for consultants
- Pod (cohort) management
- AI Matching UI with score tuning, pipeline funnel, and match reasoning
- QC Dashboard with metrics, issues, and performance tracking
- Talent Hub — client-facing candidate browser
- WynTrack — time tracking system
- Session management for training

**Tech stack:** React 18, React Router DOM 6, Tailwind CSS 3, Axios, Recharts, Radix UI, Playwright (E2E tests)

### auto-matching-service — AI Matching Engine

3-layer AI-powered candidate-job matching pipeline with its own backend and frontend.

**Matching pipeline:**

```
Input (candidate or job)
    │
    ▼
┌──────────────────┐
│  Layer 1: Filter │  SQL-based elimination (employer blocklist, job recency,
│  (hard_filter)   │  experience level). Returns up to 8000 candidates.
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  Layer 2: Embed  │  Cosine similarity via pgvector ANN search on
│  (semantic)      │  OpenAI text-embedding-3-small vectors. Returns top-k.
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  Layer 3: LLM    │  Cerebras gpt-oss-120b scoring with structured prompts.
│  (llm_scorer)    │  Returns: match_score, skills gaps, strengths, concerns.
└────────┬─────────┘
         │
         ▼
   Ranked Results (cached in DB + Redis)
```

**Additional scoring:** Rule-based deterministic scorer with 6 weighted factors (title match, skills, experience, salary, location, keywords) running alongside the LLM layer.

**Backend:** FastAPI, SQLAlchemy async, pgvector, OpenAI embeddings, Cerebras LLM, Redis caching

**Frontend:** Next.js 16, React 19, TypeScript, Tailwind v4, shadcn/ui, React Query, Recharts

---

## Database

All services share a single PostgreSQL database on Cloud SQL.

| Environment | Database | Instance |
|-------------|----------|----------|
| Production  | `smo`    | `student-marketing-operations:asia-south1:smo` |
| Test        | `smo_test` | Same instance |

- **be-fastapi-smo**: 31 models, 48 Alembic migrations (version table: `alembic_version`)
- **auto-matching-service**: Separate Alembic config (version table: `alembic_version_auto_matcher`) to avoid migration conflicts. Uses read-only mapped classes for shared SMO tables.

---

## Getting Started

### Clone

```bash
git clone --recursive git@github.com:bharat-sketch/smo-monolith.git
cd smo-monolith
```

If you already cloned without `--recursive`:
```bash
git submodule update --init --recursive
```

### Local Development

Each service runs independently. You need a PostgreSQL database with the SMO schema.

**Backend (port 8000):**
```bash
cd be-fastapi-smo
pip install -r requirements.txt
# Set DATABASE_URL in .env
alembic upgrade head
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend (port 3000):**
```bash
cd fe-react-smo
npm install
npm run start
```

**Auto-Matching Backend (port 8002):**
```bash
cd auto-matching-service
pip install -r requirements.txt
# Set DATABASE_URL, OPENAI_API_KEY, CEREBRAS_API_KEY in .env
alembic upgrade head
uvicorn app.main:app --reload --host 0.0.0.0 --port 8002
```

**Auto-Matching Frontend (port 3001):**
```bash
cd auto-matching-service/frontend
npm install
npm run dev
```

### Environment Variables

**be-fastapi-smo:**
| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | Yes | `postgresql+asyncpg://user:pass@host/db` |
| `OPENAI_API_KEY` | No | For semantic search / embeddings |
| `APIFY_API_TOKEN` | No | For job scraping |
| `MAILGUN_API_KEY` | No | For transactional emails |
| `MAILGUN_DOMAIN` | No | Mailgun sending domain |
| `GOOGLE_DRIVE_CREDENTIALS_JSON` | No | Service account JSON for Drive |
| `SHARED_DRIVE_ID` | No | Google Shared Drive ID |
| `ENABLE_SEMANTIC_SEARCH` | No | `True` to enable vector search |
| `FRONTEND_URL` | No | Frontend origin (default: `https://app.wynisco.com`) |

**auto-matching-service:**
| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | Yes | Same PostgreSQL database |
| `OPENAI_API_KEY` | Yes | For embedding generation |
| `CEREBRAS_API_KEY` | Yes | For LLM scoring |
| `REDIS_URL` | No | Falls back to DB-only cache |

---

## Deployment

### Production (App Engine)

Backend and frontend deploy as separate App Engine services:

```bash
# Backend
cd be-fastapi-smo
gcloud app deploy

# Frontend
cd fe-react-smo
npm run build
gcloud app deploy
```

### Test Environment (Cloud Run)

Single container combining nginx (React static files) + uvicorn (FastAPI) on Cloud Run.

**URL:** `https://smo-test-101215158180.asia-south1.run.app`

**Build and deploy:**
```bash
# From monolith root
gcloud builds submit --tag asia-south1-docker.pkg.dev/student-marketing-operations/smo-test/smo-test:latest
gcloud run deploy smo-test --image asia-south1-docker.pkg.dev/student-marketing-operations/smo-test/smo-test:latest --region asia-south1
```

**Configuration:**
- 2 CPU, 2 GiB RAM, scale 0–3 instances
- `--no-cpu-throttling` required (Python imports take 30s+ with throttled CPU)
- Cloud SQL socket connection via `--add-cloudsql-instances`
- Secrets injected from GCP Secret Manager
- Mailgun intentionally omitted to prevent test emails

**Teardown:**
```bash
gcloud run services delete smo-test --region asia-south1
```

---

## Testing

**Backend unit/integration tests:**
```bash
cd be-fastapi-smo
TEST_BASE_URL=http://localhost:8000 TEST_EMAIL=you@wynisco.com TEST_PASSWORD=pass pytest tests/ -v
```

13 test modules covering auth, jobs, users, employers, interviews, health, WynTrack, and more.

**Frontend E2E tests:**
```bash
cd fe-react-smo
npm run test:e2e
```

---

## Working with Submodules

Each service directory is a git submodule pointing to its own repo:

| Directory | Repository |
|-----------|------------|
| `be-fastapi-smo` | `Wynisco-Engineering/be-fastapi-smo` |
| `fe-react-smo` | `Wynisco-Engineering/fe-react-smo` |
| `auto-matching-service` | `bharat-sketch/auto-matching-service` |

**Making changes in a submodule:**
```bash
cd be-fastapi-smo
git checkout main                    # avoid detached HEAD
# ... make changes ...
git add . && git commit -m "Fix bug"
git push                             # push to submodule remote

cd ..                                # back to monolith
git add be-fastapi-smo               # update pointer
git commit -m "Update be-fastapi-smo"
git push                             # push monolith
```

**Pulling latest:**
```bash
git pull --recurse-submodules
```

**Updating all submodules to latest remote:**
```bash
git submodule update --remote --merge
git add be-fastapi-smo fe-react-smo auto-matching-service
git commit -m "Update all submodules to latest"
```

**Golden rule:** Always push the submodule first, then the monolith.

---

## Technical Notes

- pgvector returns numpy float32 — always convert with `[float(x) for x in vec]`
- asyncpg doesn't support `::vector` cast — use `CAST(:param AS vector)` instead
- OpenAI batch embedding limit ~300K tokens — `EMBEDDING_BATCH_SIZE=256` works safely
- Cloud Run test env requires `--no-cpu-throttling` due to heavy Python import times on cold start

---

## Project Structure

```
smo-monolith/
├── be-fastapi-smo/                 # Backend submodule
│   ├── app/
│   │   ├── api/v1/                 # 34 route handlers
│   │   ├── crud/                   # Database query logic
│   │   ├── models/                 # 31 SQLAlchemy models
│   │   ├── schemas/                # Pydantic request/response schemas
│   │   ├── core/                   # Config, DB, auth, rate limiter
│   │   ├── credentials/            # Auth utilities
│   │   └── utils/                  # Integrations (Drive, GCS, Apify, OpenAI, Mailgun)
│   ├── alembic/                    # 48 migration files
│   ├── tests/                      # 13 test modules
│   └── app.yaml                    # App Engine production config
│
├── fe-react-smo/                   # Frontend submodule
│   ├── src/
│   │   ├── pages/                  # Route pages
│   │   ├── components/             # Reusable UI components
│   │   ├── services/               # API client modules
│   │   └── context/                # React context providers
│   ├── e2e/                        # Playwright E2E tests
│   └── app.yaml                    # App Engine production config
│
├── auto-matching-service/          # AI Matching submodule
│   ├── app/
│   │   ├── api/v1/                 # 3 routers (matching, embeddings, listing)
│   │   ├── services/               # Matching engine, scorers, embeddings
│   │   ├── models/                 # DB models + read-only shared models
│   │   └── core/                   # Config, DB, Redis
│   ├── frontend/                   # Next.js 16 dashboard
│   └── scripts/                    # Job scraping and re-embedding utilities
│
├── Dockerfile                      # Combined Cloud Run container
├── nginx.conf                      # nginx reverse proxy config
├── start.py                        # Container startup (nginx + uvicorn)
├── .gcloudignore                   # Cloud Build upload filter
├── .dockerignore                   # Docker build context filter
└── CLAUDE.md                       # AI assistant project context
```
