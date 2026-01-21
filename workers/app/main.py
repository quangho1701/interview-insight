"""Celery worker application entry point."""

from celery import Celery

from app.core.config import get_settings

settings = get_settings()

# Initialize Celery app - name MUST match API producer
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
    result_expires=86400,
    # Worker-specific settings
    worker_prefetch_multiplier=1,  # Fair task distribution
    task_acks_late=True,  # Acknowledge after task completion
    # Timeout settings for long-running ML tasks
    task_time_limit=3600,  # Hard limit: 60 minutes (kills task)
    task_soft_time_limit=3300,  # Soft limit: 55 minutes (raises SoftTimeLimitExceeded)
    task_track_started=True,  # Track task state as STARTED
)

# Import tasks to register them with Celery
from app import tasks  # noqa: F401, E402
