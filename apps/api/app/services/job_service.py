"""Service for job operations."""

from typing import Optional
from uuid import UUID

from sqlmodel import Session

from app.models.processing_job import ProcessingJob


class JobService:
    """Service for job-related operations."""

    def __init__(self, session: Session):
        """Initialize with database session."""
        self.session = session

    def get_job(self, job_id: UUID) -> Optional[ProcessingJob]:
        """Retrieve a job by ID.

        Args:
            job_id: UUID of the job to retrieve.

        Returns:
            ProcessingJob if found, None otherwise.
        """
        return self.session.get(ProcessingJob, job_id)

    def get_job_for_user(
        self, job_id: UUID, user_id: UUID
    ) -> Optional[ProcessingJob]:
        """Retrieve a job by ID, verifying user ownership.

        Args:
            job_id: UUID of the job to retrieve.
            user_id: UUID of the requesting user.

        Returns:
            ProcessingJob if found and owned by user, None otherwise.
        """
        job = self.get_job(job_id)
        if job and job.user_id == user_id:
            return job
        return None
