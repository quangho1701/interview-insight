# Phase 5 Implementation Plan: Summarization & Transcription

**Objective:** Implement the ML pipeline for transcribing audio and generating summaries using `faster-whisper` and `Llama 3.3 8B`.

**Context:** The Worker service exists (Phase 4). We are now filling in the "stubbed" processing logic.

## 1. Prerequisites & Environment Setup

### 1.1 Update Dependencies
Modify `workers/pyproject.toml` (or `requirements.txt`) to include:
- `faster-whisper`
- `torch` (with CUDA support)
- `transformers`
- `accelerate`
- `bitsandbytes`

### 1.2 Docker Configuration
Ensure `workers/Dockerfile` installs system dependencies required for handling audio (e.g., `ffmpeg`).
- **Action:** Add `RUN apt-get update && apt-get install -y ffmpeg` to the Dockerfile.

## 2. Core Service Implementation

### 2.1 Transcription Service
**File:** `workers/app/services/transcription.py`
**Class:** `TranscriptionService`
- **Method:** `transcribe(audio_path: str) -> dict`
- **Logic:**
    - Initialize `WhisperModel("large-v3", device="cuda", compute_type="float16")`.
    - Run `.transcribe()` on the audio file.
    - Return structured data: `text` (full text) and `segments` (list with timestamps).

### 2.2 Summarization Service
**File:** `workers/app/services/summarization.py`
**Class:** `SummarizationService`
- **Method:** `summarize(transcript: str) -> dict`
- **Logic:**
    - Load `meta-llama/Meta-Llama-3-8B-Instruct` (using 4-bit quantization).
    - **Prompt:** Construct a prompt that asks for JSON output with keys: `summary`, `key_topics`, `sentiment_score` (0-10), `strengths`, `weaknesses`.
    - **Parsing:** Ensure the output is valid JSON. Use a retry mechanism or a constrained generation library if possible (but raw prompting is fine for Phase 5 MVP).

## 3. Celery Task Integration

### 3.1 Update Job Processor
**File:** `workers/app/tasks.py`
**Function:** `process_interview(job_id: str)`
- **Current State:** Stubs.
- **New Flow:**
    1.  **Fetch Job:** Get job from DB.
    2.  **Download:** Download audio file from S3 to a temporary local path.
    3.  **Transcribe:** Call `TranscriptionService.transcribe()`.
    4.  **Summarize:** Call `SummarizationService.summarize()`.
    5.  **Save:** Update `InterviewAnalysis` table in Postgres with the JSON results.
    6.  **Cleanup:** Delete local temp file.
    7.  **Finalize:** Update Job Status to `COMPLETED`.

## 4. Testing Plan

### 4.1 Unit Tests
- `tests/unit/test_transcription.py`: Mock the `WhisperModel` and verify `transcribe` returns expected format.
- `tests/unit/test_summarization.py`: Mock the LLM pipeline and verify prompt construction and JSON parsing.

### 4.2 Integration Tests
- **End-to-End:**
    - Upload a small 30s sample WAV file.
    - Wait for Job `COMPLETED`.
    - Query DB: Check `metrics_json` contains "Executive Summary" and `transcript` is accurate.

## 5. Definition of Done
- Worker builds successfully with new ML dependencies.
- Audio is successfully transcribed (text is legible).
- Summary is generated and makes sense.
- Data is persisted to Postgres.
- Audio file is deleted from local disk after processing.
