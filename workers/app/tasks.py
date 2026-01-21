"""Celery task definitions for interview processing."""

import json
import logging
import os
import tempfile
from datetime import datetime, timezone
from enum import Enum
from uuid import uuid4

from celery.exceptions import SoftTimeLimitExceeded
from sqlmodel import text

from app.core.database import get_session
from app.main import celery_app
from app.services.s3 import S3Service
from app.services.transcription import TranscriptionService
from app.services.summarization import SummarizationService

# Configure logging
logger = logging.getLogger(__name__)

# Transient errors that should trigger retries (keep PROCESSING status)
TRANSIENT_ERRORS = (ConnectionError, TimeoutError, OSError)

# Lazy-initialized service instances (loaded once per worker)
_transcription_service: TranscriptionService | None = None
_summarization_service: SummarizationService | None = None
_s3_service: S3Service | None = None


def get_transcription_service() -> TranscriptionService:
    """Get or create the transcription service singleton."""
    global _transcription_service
    if _transcription_service is None:
        _transcription_service = TranscriptionService()
    return _transcription_service


def get_summarization_service() -> SummarizationService:
    """Get or create the summarization service singleton."""
    global _summarization_service
    if _summarization_service is None:
        _summarization_service = SummarizationService()
    return _summarization_service


def get_s3_service() -> S3Service:
    """Get or create the S3 service singleton."""
    global _s3_service
    if _s3_service is None:
        _s3_service = S3Service()
    return _s3_service


class JobStatus(str, Enum):
    """Processing job status - must match API enum."""

    PENDING = "pending"
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


def _update_job_failed(job_id: str, error_message: str) -> None:
    """Update job status to FAILED with error message."""
    try:
        with get_session() as session:
            session.execute(
                text("""
                    UPDATE processing_jobs
                    SET status = :status, error_message = :error, updated_at = :updated_at
                    WHERE id = :job_id
                """),
                {
                    "status": JobStatus.FAILED.value,
                    "error": error_message[:500],
                    "updated_at": datetime.now(timezone.utc),
                    "job_id": job_id,
                },
            )
            session.commit()
    except Exception as db_exc:
        logger.error(f"Failed to update job status: {db_exc}")


@celery_app.task(
    name="vibecheck.tasks.process_interview",
    bind=True,
    max_retries=3,
    default_retry_delay=60,
)
def process_interview(self, job_id: str) -> dict:
    """Process an interview recording.

    Pipeline:
    1. Download audio from S3
    2. Transcribe using faster-whisper
    3. Summarize using Llama 3.3 8B
    4. Create InterviewAnalysis record
    5. Update job with analysis_id

    Args:
        job_id: UUID string of the ProcessingJob.

    Returns:
        Dict with processing result status.
    """
    logger.info(f"Starting processing for job {job_id}")
    local_audio_path = None

    try:
        # Get job details
        with get_session() as session:
            result = session.execute(
                text("""
                    SELECT s3_audio_key, user_id, interviewer_id
                    FROM processing_jobs
                    WHERE id = :job_id
                """),
                {"job_id": job_id},
            )
            row = result.fetchone()
            if not row:
                raise ValueError(f"Job {job_id} not found")

            s3_audio_key = row[0]
            user_id = row[1]
            interviewer_id = row[2]

            if not interviewer_id:
                raise ValueError(f"Job {job_id} missing interviewer_id")

            # Update status to PROCESSING
            session.execute(
                text("""
                    UPDATE processing_jobs
                    SET status = :status, updated_at = :updated_at
                    WHERE id = :job_id
                """),
                {
                    "status": JobStatus.PROCESSING.value,
                    "updated_at": datetime.now(timezone.utc),
                    "job_id": job_id,
                },
            )
            session.commit()
            logger.info(f"Job {job_id} status updated to PROCESSING")

        # Step 1: Download audio from S3
        logger.info(f"Downloading audio: {s3_audio_key}")
        s3_service = get_s3_service()
        local_audio_path = os.path.join(
            tempfile.gettempdir(),
            f"vibecheck_{job_id}_{uuid4().hex[:8]}.audio"
        )
        s3_service.download_file(s3_audio_key, local_audio_path)

        # Step 2: Transcribe audio
        logger.info("Starting transcription...")
        transcription_service = get_transcription_service()
        transcript = transcription_service.transcribe(local_audio_path)
        logger.info(f"Transcription complete: {len(transcript)} characters")

        # Step 3: Summarize transcript
        logger.info("Starting summarization...")
        summarization_service = get_summarization_service()
        summary = summarization_service.summarize(transcript)
        logger.info("Summarization complete")

        # Step 4: Create InterviewAnalysis record (idempotent via job_id)
        analysis_id = str(uuid4())
        metrics_json = {
            "executive_summary": summary["executive_summary"],
            "key_topics": summary["key_topics"],
            "strengths": summary["strengths"],
            "areas_for_improvement": summary["areas_for_improvement"],
        }

        with get_session() as session:
            session.execute(
                text("""
                    INSERT INTO interview_analyses
                    (id, job_id, user_id, interviewer_id, sentiment_score, summary, metrics_json, transcript_redacted, created_at, updated_at)
                    VALUES (:id, :job_id, :user_id, :interviewer_id, :sentiment_score, :summary, :metrics_json, :transcript, :now, :now)
                    ON CONFLICT (job_id) DO UPDATE SET
                        sentiment_score = EXCLUDED.sentiment_score,
                        summary = EXCLUDED.summary,
                        metrics_json = EXCLUDED.metrics_json,
                        transcript_redacted = EXCLUDED.transcript_redacted,
                        updated_at = EXCLUDED.updated_at
                """),
                {
                    "id": analysis_id,
                    "job_id": job_id,
                    "user_id": str(user_id),
                    "interviewer_id": str(interviewer_id),
                    "sentiment_score": summary["sentiment_score"],
                    "summary": summary["executive_summary"],
                    "metrics_json": json.dumps(metrics_json),
                    "transcript": transcript,
                    "now": datetime.now(timezone.utc),
                },
            )
            session.commit()

            # Get the actual analysis_id (might be existing on conflict)
            result = session.execute(
                text("SELECT id FROM interview_analyses WHERE job_id = :job_id"),
                {"job_id": job_id},
            )
            analysis_id = str(result.scalar())
            logger.info(f"Created/updated InterviewAnalysis: {analysis_id}")

        # Step 5: Update job with analysis_id and mark COMPLETED
        with get_session() as session:
            session.execute(
                text("""
                    UPDATE processing_jobs
                    SET status = :status, analysis_id = :analysis_id, updated_at = :updated_at
                    WHERE id = :job_id
                """),
                {
                    "status": JobStatus.COMPLETED.value,
                    "analysis_id": analysis_id,
                    "updated_at": datetime.now(timezone.utc),
                    "job_id": job_id,
                },
            )
            session.commit()
            logger.info(f"Job {job_id} completed successfully")

        return {"status": "completed", "job_id": job_id, "analysis_id": analysis_id}

    except SoftTimeLimitExceeded:
        # Task timed out - permanent failure, do not retry
        logger.error(f"Job {job_id} timed out (soft time limit exceeded)")
        _update_job_failed(job_id, "Processing timed out after 55 minutes")
        return {"status": "failed", "job_id": job_id, "error": "timeout"}

    except TRANSIENT_ERRORS as exc:
        # Transient error - keep PROCESSING status and retry
        logger.warning(
            f"Job {job_id} encountered transient error: {exc}. "
            f"Retry {self.request.retries + 1}/{self.max_retries}"
        )
        # Do NOT update status to FAILED - keep as PROCESSING for retry
        raise self.retry(exc=exc)

    except Exception as exc:
        # Permanent error - mark as FAILED, do not retry
        logger.error(f"Job {job_id} failed with permanent error: {exc}")
        _update_job_failed(job_id, str(exc))
        # Do not retry permanent errors
        return {"status": "failed", "job_id": job_id, "error": str(exc)}

    finally:
        # Cleanup temp file
        if local_audio_path and os.path.exists(local_audio_path):
            try:
                os.remove(local_audio_path)
                logger.info(f"Cleaned up temp file: {local_audio_path}")
            except OSError as e:
                logger.warning(f"Failed to cleanup temp file: {e}")
