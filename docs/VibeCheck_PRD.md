# Product Requirements Document (PRD): VibeCheck

## 1. Product Overview

### Vision
**VibeCheck** is an AI-powered intelligence platform that democratizes the "black box" of job interviews. By analyzing the emotional state, communication style, and behavioral "vibe" of interviewers, we create a searchable, data-driven transparency layer for the hiring process.

### Core Goals
1.  **Empower Candidates:** Provide actionable insights into an interviewer's style.
2.  **Quantify "Vibe":** Objective metrics (interruption rate, sentiment volatility) over subjective reviews.
3.  **Safe Community:** Ensure data integrity via strict aggregation thresholds to prevent review bombing.

### Target Audience
*   **Primary:** Job Seekers (SWEs, PMs, Designers).
*   **Secondary:** Hiring Managers seeking data-driven feedback.

---

## 2. File Structure & Naming Patterns

### Repository Organization
Monorepo structure using Turborepo.

> [!IMPORTANT]
> **Database Decision:** We are using **SQLModel** (SQLAlchemy + Pydantic) within the Python service for tight integration with our ML models. No separate Node.js ORM.

```text
vibecheck/
├── apps/
│   ├── web/                 # Next.js 14 (App Router) - User Facing App
│   │   ├── src/
│   │   │   ├── app/         # Routes
│   │   │   ├── components/  # Local components
│   │   │   └── lib/         # Utility functions
│   └── api/                 # FastAPI (Python) - Core Business Logic
│       ├── app/
│       │   ├── core/        # Config, Security
│       │   ├── api/         # Endpoints (v1)
│       │   ├── models/      # SQLModel Definitions (DB Schema)
│       │   ├── services/    # Business Logic (Uploads, Auth)
│       │   └── worker/      # Celery/Redis Tasks producer
│       └── alembic/         # DB Migrations
├── workers/                 # ML Worker (Python/GPU Optimized)
│   ├── src/
│   │   ├── ml/              # Pyannote/Whisper Inference
│   │   └── tasks.py         # Job Consumer Logic
│   └── Dockerfile.gpu
├── packages/
│   ├── ui/                  # Shared UI Component Library
│   └── types/               # Shared logic
└── docker/                  # Docker Compose (Redis, Postgres, API, Worker)
```

### Naming Conventions
*   **Python:** `snake_case` (e.g., `audio_processor.py`, `calculate_sentiment`).
*   **TS/JS:** `kebab-case` for files, `camelCase` for variables.
*   **Commits:** Conventional Commits.

---

## 3. UI Design

### Brand Aesthetic
*   **Theme:** "Professional Futurism". Dark mode (`#0a0a0a`) with "Aura" gradients.
*   **Visuals:** Glassmorphism, smooth spline charts. Use `lucide-react` for icons.

### Layout Principles
1.  **Dashboard:** Focus on "Feed" or "Analysis Results".
2.  **Interviewer Profile:** Hero section with "Vibe Avatar". Aggregated stats require >3 data points to view.
3.  **Upload Flow:** Minimalist. Drag-and-drop.

---

## 4. Key Features & User Flow

### Core Functionality
1.  **Upload & Transcribe:** Async flow. User uploads -> Job Queued -> Notification when ready.
2.  **Vibe Analysis Engine:** Speaker Diarization + Sentiment Analysis + Behavioral Tagging.
3.  **Trust System:**
    *   **Aggregation Threshold:** Public profiles for interviewers only appear after **3 distinct user uploads**.
    *   **Private vs Public:** Data is private to the uploader until the threshold is met.

### User Journey Map

**Step 1: Onboarding**
*   Sign up (GitHub/LinkedIn).
*   Complete Calibration Profile.

**Step 2: Submission**
*   Upload audio.
*   System validates file. User tags Interviewer (Mandatory).
*   **Status:** "Queued for Analysis".

**Step 3: Async Processing**
*   **Worker:** Picks up job -> Transcribes (Whisper) -> Diarizes (pyannote) -> Maps Sentiment.
*   **Result:** Written to DB. Notification sent to user.

**Step 4: Review**
*   User reviews private summary.
*   User confirms identification.
*   **Data Policy:** Original audio is **deleted immediately** after analysis. Only metrics/text retained.

**Step 5: Discovery**
*   Search for "Jane Doe".
*   If count < 3: "Not enough data yet."
*   If count >= 3: Display aggregated Vibe Profile.

---

## 5. Backend Architecture & Infrastructure

### Tech Stack
*   **API:** FastAPI (Python) - Lightweight, handles auth & CRUD.
*   **Worker:** Python + GPU Support (RunPod/Modal/AWS GPU).
*   **Queue:** Redis (Task Broker).
*   **Database:** PostgreSQL (via SQLModel).
*   **Migrations:** Alembic.
*   **Storage:** AWS S3 (Presigned URLs).

### Architecture Diagram (Text)
`[Client] -> [Next.js App] -> [FastAPI] -> [Redis Queue] -> [GPU Worker]`
`[GPU Worker] -> [S3 (Read Audio)] -> [Inference] -> [Postgres (Write Results)]`

### Database Schema (SQLModel)
*   **User:** `id`, `provider`, `credits`.
*   **Interviewer:** `id`, `name`, `company`, `profile_status` (HIDDEN/PUBLIC).
*   **InterviewAnalysis:** `id`, `user_id`, `interviewer_id`, `metrics_json`, `sentiment_score`.
*   **ProcessingJob:** `id`, `status` (PENDING, PROCESSING, COMPLETED, FAILED).

---

## 6. Constraints

### Technical
*   **GPU Dependency:** Analysis requires GPU acceleration. Cannot run on standard CPU instances efficiently.
*   **Queue-Based:** No synchronous analysis results. All processing is backgrounded.

### Legal & Trust
*   **Aggregated Anonymity:** Public data is strictly aggregated. No single review can define a public profile.
*   **Audio Deletion:** Raw audio is ephemeral. It exists only for the duration of the processing job.

---

## 7. Security

### Data Protection
*   **Zero Retention (Audio):** Workers are configured to wipe local and S3 copies of audio immediately upon job completion.
*   **PII Handling:** Since we delete audio, we focus on text redaction for the private transcript.
    *   NER (Named Entity Recognition) runs on transcript to mask names/numbers.
*   **Row Level Security:** Users strictly access only their own submisisons.
