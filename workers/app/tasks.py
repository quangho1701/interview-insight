"""Celery task definitions for interview processing."""

import logging
import time
from datetime import datetime, timezone
from enum import Enum

from sqlmodel import text

from app.core.database import get_session
from app.main import celery_app

# Configure logging
logger = logging.getLogger(__name__)


class JobStatus(str, Enum):
    """Processing job status - must match API enum."""

    PENDING = "pending"
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


@celery_app.task(
    name="vibecheck.tasks.process_interview",
    bind=True,
    max_retries=3,
    default_retry_delay=60,
)
def process_interview(self, job_id: str) -> dict:
    """Process an interview recording.

    This is a stub implementation that simulates processing.
    Future phases will add:
    - Whisper transcription
    - Speaker diarization
    - Sentiment analysis
    - Metrics calculation

    Args:
        job_id: UUID string of the ProcessingJob.

    Returns:
        Dict with processing result status.
    """
    logger.info(f"Starting processing for job {job_id}")

    try:
        with get_session() as session:
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

        # Simulate processing work (placeholder for ML pipeline)
        logger.info(f"Simulating processing for job {job_id}...")
        time.sleep(5)  # Simulate 5 seconds of work

        with get_session() as session:
            # Update status to COMPLETED
            session.execute(
                text("""
                    UPDATE processing_jobs
                    SET status = :status, updated_at = :updated_at
                    WHERE id = :job_id
                """),
                {
                    "status": JobStatus.COMPLETED.value,
                    "updated_at": datetime.now(timezone.utc),
                    "job_id": job_id,
                },
            )
            session.commit()
            logger.info(f"Job {job_id} completed successfully")

        return {"status": "completed", "job_id": job_id}

    except Exception as exc:
        logger.error(f"Job {job_id} failed with error: {exc}")

        # Update job to FAILED status
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
                        "error": str(exc)[:500],  # Truncate error message
                        "updated_at": datetime.now(timezone.utc),
                        "job_id": job_id,
                    },
                )
                session.commit()
        except Exception as db_exc:
            logger.error(f"Failed to update job status: {db_exc}")

        # Re-raise for Celery retry mechanism
        raise self.retry(exc=exc)
