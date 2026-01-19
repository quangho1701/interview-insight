"""Celery application configuration for task production."""

from celery import Celery

from app.core.config import get_settings

settings = get_settings()

# Initialize Celery app - name MUST match worker's app name
celery_app = Celery(
    "vibecheck",
    broker=settings.get_redis_url(),
    backend=settings.get_redis_url(),
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    # Task result expiration (24 hours)
    result_expires=86400,
    # Prevent task execution on producer side
    task_always_eager=False,
)

# Task name constants for type safety
TASK_PROCESS_INTERVIEW = "vibecheck.tasks.process_interview"


def enqueue_interview_processing(job_id: str) -> str:
    """Enqueue an interview processing task.

    Args:
        job_id: UUID string of the ProcessingJob to process.

    Returns:
        Celery task ID.
    """
    result = celery_app.send_task(
        TASK_PROCESS_INTERVIEW,
        args=[job_id],
    )
    return result.id
