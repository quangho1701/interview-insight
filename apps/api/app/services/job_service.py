"""Service for job operations."""

from typing import Optional
from uuid import UUID

from sqlmodel import Session, func, select

from app.models.enums import JobStatus
from app.models.interviewer import Interviewer
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

    def list_for_user(
        self,
        user_id: UUID,
        status: Optional[JobStatus] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[dict], int]:
        """List jobs for a user with optional status filter and pagination.

        Args:
            user_id: UUID of the user.
            status: Optional status filter.
            limit: Maximum number of items to return.
            offset: Number of items to skip.

        Returns:
            Tuple of (list of job dicts with interviewer name, total count).
        """
        # Build base condition
        conditions = [ProcessingJob.user_id == user_id]
        if status:
            conditions.append(ProcessingJob.status == status)

        # Count total
        count_stmt = (
            select(func.count())
            .select_from(ProcessingJob)
            .where(*conditions)
        )
        total = self.session.exec(count_stmt).one()

        # Fetch items with interviewer name via outer join
        stmt = (
            select(ProcessingJob, Interviewer.name)
            .outerjoin(Interviewer, ProcessingJob.interviewer_id == Interviewer.id)
            .where(*conditions)
            .order_by(ProcessingJob.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        results = self.session.exec(stmt).all()

        items = []
        for job, interviewer_name in results:
            items.append({
                "job_id": job.id,
                "status": job.status,
                "interviewer_id": job.interviewer_id,
                "interviewer_name": interviewer_name,
                "error_message": job.error_message,
                "created_at": job.created_at,
                "updated_at": job.updated_at,
            })

        return items, total
