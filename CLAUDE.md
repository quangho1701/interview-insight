# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

VibeCheck is an AI-powered interview analysis platform built as a full-stack monorepo. Users upload interview recordings which are transcribed, analyzed for sentiment and metrics, and aggregated into interviewer profiles.

**Stack:** FastAPI (Python) backend, Next.js 14 frontend (scaffold), PostgreSQL, Redis, ML worker (planned)

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
pytest                          # Run all tests
pytest tests/unit/              # Unit tests only
pytest tests/integration/       # Integration tests only
pytest -k "test_name"           # Run specific test
pytest --cov                    # Run with coverage
alembic upgrade head            # Apply migrations
alembic revision -m "message"   # Create migration
uvicorn app.main:app --reload   # Run dev server (port 8000)
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
│   │       └── endpoints/      # Route handlers (login, uploads)
│   ├── core/                   # config.py, database.py, security.py
│   ├── models/                 # SQLModel ORM (User, Interviewer, InterviewAnalysis, ProcessingJob)
│   ├── schemas/                # Pydantic request/response schemas
│   ├── services/               # Business logic (s3_service.py)
│   └── main.py                 # FastAPI app, CORS, health check
├── tests/
│   ├── conftest.py             # Fixtures: db_session, client (transactional rollback)
│   ├── unit/                   # Model and config tests
│   └── integration/            # API endpoint tests
└── alembic/                    # Database migrations

apps/web/                       # Next.js frontend (scaffold only)
workers/                        # ML processing worker (planned - Whisper, diarization, sentiment)
packages/                       # Shared libs (types, ui) - planned
```

## Key Patterns

### API Structure
- **Router pattern:** Endpoints in `api/v1/endpoints/` are aggregated by `api/v1/router.py` and mounted at `/api/v1`
- **Dependency injection:** Use type aliases from `api/deps.py`:
  - `CurrentUser` - authenticated user from JWT
  - `SessionDep` - database session
  - `S3ServiceDep` - S3 service instance

### Configuration
- Pydantic Settings with `get_settings()` cached via `@lru_cache`
- Environment variables loaded from `.env` file (see config.py for all options)
- Test env uses different ports: DATABASE_PORT=5433, REDIS_PORT=6380

### Database
- SQLModel ORM with mixins in `models/base.py` (UUIDMixin, TimestampMixin)
- All models use UUID primary keys
- Enums in `models/enums.py` (AuthProvider, JobStatus, ProfileStatus)

### Testing
- Fixtures in `conftest.py` provide transactional sessions with automatic rollback
- `db_session` fixture uses SAVEPOINT for nested transactions
- `client` fixture overrides `get_session` dependency

### File Upload Flow
1. Client requests presigned URL via `/api/v1/uploads/presign`
2. Client uploads directly to S3 using presigned URL
3. Client confirms upload via `/api/v1/uploads/confirm` → creates ProcessingJob

## Naming Conventions

- **Python:** snake_case for files and functions
- **TypeScript:** kebab-case for files, camelCase for variables
- **Git:** Conventional Commits
