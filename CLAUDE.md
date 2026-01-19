# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

VibeCheck is an AI-powered interview analysis platform built as a full-stack monorepo. Users upload interview recordings which are transcribed, analyzed for sentiment and metrics, and aggregated into interviewer profiles.

**Stack:** FastAPI (Python) backend, Next.js 14 frontend (App Router), PostgreSQL, Redis, Celery ML worker

## Commands

### Root Level (Turborepo + pnpm)
```bash
pnpm build          # Build all packages
pnpm dev            # Dev mode for all apps
pnpm lint           # Lint all packages
pnpm test           # Run all tests
pnpm format         # Prettier format
```

### Backend (apps/api)
```bash
cd apps/api
pip install -e ".[dev]"                     # Install with dev dependencies
pytest                                      # Run all tests
pytest tests/unit/                          # Unit tests only
pytest tests/integration/                   # Integration tests only
pytest -k "test_name"                       # Run specific test
pytest --cov                                # Run with coverage
alembic upgrade head                        # Apply migrations
alembic revision --autogenerate -m "msg"    # Create migration (auto-detect changes)
uvicorn app.main:app --reload               # Run dev server (port 8000)
```

### Frontend (apps/web)
```bash
cd apps/web
pnpm dev                        # Run Next.js dev server (port 3000)
pnpm build                      # Build for production
pnpm lint                       # Run ESLint
```

### UI Package (packages/ui)
```bash
cd packages/ui
pnpm storybook                  # Run Storybook dev server (port 6006)
pnpm build-storybook            # Build static Storybook
```

### Worker (workers)
```bash
cd workers
pip install -e .                            # Install base dependencies
pip install -e ".[ml]"                      # Install with ML dependencies (CUDA recommended)
celery -A app.main worker --loglevel=info   # Run Celery worker
```

### Docker
```bash
docker-compose -f docker/docker-compose.yml up      # Production (Postgres:5432, Redis:6379)
docker-compose -f docker/docker-compose.test.yml up # Test (Postgres:5433, Redis:6380)
```

## Architecture

```
apps/api/                       # FastAPI backend
├── app/
│   ├── api/
│   │   ├── deps.py             # Dependency injection (CurrentUser, SessionDep, S3ServiceDep)
│   │   └── v1/
│   │       ├── router.py       # Aggregates all endpoint routers
│   │       └── endpoints/      # Route handlers (login, uploads, jobs, interviewers, analysis)
│   ├── core/                   # config.py, database.py, security.py
│   ├── models/                 # SQLModel ORM (User, Interviewer, InterviewAnalysis, ProcessingJob)
│   ├── schemas/                # Pydantic request/response schemas
│   ├── services/               # Business logic (s3_service.py, job_service.py, interviewer_service.py)
│   └── main.py                 # FastAPI app, CORS, health check
├── tests/
│   ├── conftest.py             # Fixtures: db_session, client (transactional rollback)
│   ├── unit/                   # Model and config tests
│   └── integration/            # API endpoint tests
└── alembic/                    # Database migrations

apps/web/                       # Next.js 14 frontend (App Router)
├── src/
│   ├── app/                    # App Router pages and layouts
│   │   ├── (auth)/             # Auth route group (login, signup)
│   │   └── (dashboard)/        # Dashboard route group (protected)
│   ├── components/             # React components (Sidebar, Header)
│   ├── context/                # React Context providers (AuthContext)
│   └── lib/                    # Utilities (api-client.ts, utils.ts)
workers/                        # Celery ML worker (transcription + summarization)
├── app/
│   ├── main.py                 # Celery app initialization
│   ├── tasks.py                # process_interview task
│   ├── core/                   # config.py, database.py
│   └── services/               # s3.py, transcription.py, summarization.py
└── Dockerfile                  # Python 3.11, ffmpeg, CUDA-ready

docker/                         # Docker Compose files for local dev
packages/
├── ui/                         # @vibecheck/ui component library
│   ├── src/
│   │   ├── components/         # Button, Card, Input (with *.stories.tsx)
│   │   ├── lib/utils.ts        # cn() utility for class merging
│   │   └── index.ts            # Public exports
│   ├── .storybook/             # Storybook configuration (Vite-based)
│   └── tailwind.config.ts      # Tailwind with animations plugin
└── types/                      # Shared TypeScript types (scaffold)
```

## Key Patterns

### API Structure
- **Router pattern:** Endpoints in `api/v1/endpoints/` are aggregated by `api/v1/router.py` and mounted at `/api/v1`
- **Endpoints:** `login` (auth), `uploads`, `jobs`, `interviewers`, `analysis`
- **Dependency injection:** Use type aliases from `api/deps.py`:
  - `CurrentUser` - authenticated user from JWT
  - `SessionDep` - database session
  - `S3ServiceDep` - S3 service instance

### Configuration
- Pydantic Settings with `get_settings()` cached via `@lru_cache`
- Environment variables loaded from `.env` file (see config.py for all options)
- Test env uses different ports: DATABASE_PORT=5433, REDIS_PORT=6380
- Frontend env vars in `apps/web/.env.local`: `NEXT_PUBLIC_API_URL`, `NEXT_PUBLIC_DEV_AUTH_BYPASS`

### Dev Authentication Bypass
For local development without OAuth setup:
- Backend: Set `DEV_AUTH_BYPASS=true` in `apps/api/.env` → creates guest user automatically
- Frontend: Set `NEXT_PUBLIC_DEV_AUTH_BYPASS=true` in `apps/web/.env.local` → auto-fetches dev token
- Guest user ID: `00000000-0000-0000-0000-000000000000` (defined in `core/config.py`)

### Database
- SQLModel ORM with mixins in `models/base.py` (UUIDMixin, TimestampMixin)
- All models use UUID primary keys
- Enums in `models/enums.py` (AuthProvider, JobStatus, ProfileStatus)

### Testing
- Fixtures in `conftest.py` provide transactional sessions with automatic rollback
- `db_session` fixture uses SAVEPOINT for nested transactions
- `client` fixture overrides `get_session` dependency

### File Upload Flow
1. Client requests presigned URL via `POST /api/v1/uploads/presigned-url` (creates ProcessingJob with status=PENDING)
2. Client uploads directly to S3 using presigned URL
3. Client confirms upload via `POST /api/v1/uploads/{job_id}/confirm` → sets interviewer_id → enqueues Celery task
4. Client polls job status via `GET /api/v1/jobs/{job_id}`

### Background Jobs
- Celery app configured in `core/celery_utils.py` with Redis broker
- Task enqueuing via `enqueue_interview_processing(job_id)` function
- Task name constant: `TASK_PROCESS_INTERVIEW = "vibecheck.tasks.process_interview"`

### ML Worker Pipeline
The worker (`workers/app/tasks.py`) processes interviews through:
1. Download audio from S3 to temp file
2. Transcribe using faster-whisper (distil-large-v3 model)
3. Summarize using Llama 3.3 8B (4-bit quantization)
4. Create `InterviewAnalysis` record with sentiment score and metrics
5. Update job status to COMPLETED
6. Cleanup temp file

Services are lazy-initialized as singletons per worker process. Install ML dependencies with `pip install -e ".[ml]"` in the workers directory.

### Frontend Patterns (apps/web)
- **Route groups:** `(auth)` for login/signup, `(dashboard)` for protected pages
- **Auth flow:** `AuthContext` provides `useAuth()` hook with `login()`, `logout()`, `isAuthenticated`
- **API client:** Axios instance at `lib/api-client.ts` with JWT interceptor (reads token from localStorage)
- **Protected routes:** Dashboard layout redirects to `/login` if not authenticated

### UI Components (@vibecheck/ui)
- **Styling:** Components use `class-variance-authority` (cva) for variant definitions
- **Class merging:** Use `cn()` from `lib/utils.ts` which combines `clsx` + `tailwind-merge`
- **Primitives:** Radix UI for accessible base components (`@radix-ui/react-slot`)
- **Stories:** Each component has a co-located `*.stories.tsx` file for Storybook

## Naming Conventions

- **Python:** snake_case for files and functions
- **TypeScript:** kebab-case for files, camelCase for variables
- **Git:** Conventional Commits
