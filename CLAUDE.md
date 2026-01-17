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
uvicorn app.main:app --reload   # Run dev server
```

### Docker
```bash
docker-compose -f docker/docker-compose.yml up      # Production (Postgres:5432, Redis:6379)
docker-compose -f docker/docker-compose.test.yml up # Test (Postgres:5433, Redis:6380)
```

## Architecture

```
apps/
├── api/                    # FastAPI backend (active)
│   ├── app/
│   │   ├── core/           # config.py, database.py
│   │   ├── models/         # SQLModel schemas (User, Interviewer, InterviewAnalysis, ProcessingJob)
│   │   └── main.py         # FastAPI entry point
│   ├── tests/              # pytest tests (unit + integration)
│   └── alembic/            # Database migrations
└── web/                    # Next.js frontend (scaffold only)

workers/                    # ML processing worker (planned - Whisper, diarization, sentiment)
packages/                   # Shared libs (types, ui) - planned
```

## Database Models

- **users** - OAuth users (GitHub/LinkedIn), credits system
- **interviewers** - Profile data, aggregated from analyses
- **interview_analyses** - Sentiment scores, JSONB metrics, redacted transcripts
- **processing_jobs** - Async job queue (S3 audio key, status tracking)

All models use UUID primary keys and timestamp mixins.

## Key Patterns

- **Configuration:** Pydantic Settings with `get_settings()` cached singleton
- **Database:** SQLModel ORM, async session support via `get_session()` dependency
- **Testing:** Transactional fixtures with rollback, separate test database on port 5433
- **Privacy:** Audio deleted after analysis, PII redaction planned, 3+ upload threshold for public profiles

## Naming Conventions

- **Python:** snake_case for files and functions
- **TypeScript:** kebab-case for files, camelCase for variables
- **Git:** Conventional Commits
