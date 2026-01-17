"""Database session management for Worker tasks."""

from contextlib import contextmanager
from typing import Generator

from sqlmodel import Session, create_engine

from app.core.config import get_settings


def get_engine():
    """Create database engine for worker.

    Uses pool_pre_ping to detect stale connections in long-running workers.
    """
    settings = get_settings()
    return create_engine(
        settings.database_url,
        echo=False,
        pool_pre_ping=True,
    )


@contextmanager
def get_session() -> Generator[Session, None, None]:
    """Context manager for database sessions in tasks.

    Usage:
        with get_session() as session:
            job = session.get(ProcessingJob, job_id)
            job.status = JobStatus.PROCESSING
            session.commit()
    """
    engine = get_engine()
    with Session(engine) as session:
        try:
            yield session
        except Exception:
            session.rollback()
            raise
