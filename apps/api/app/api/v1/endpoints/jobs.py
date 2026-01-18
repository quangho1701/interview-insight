"""Job status endpoints."""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status

from app.api.deps import CurrentUser, SessionDep
from app.models.enums import JobStatus
from app.schemas.job import JobListItem, JobListResponse, JobStatusResponse
from app.services.job_service import JobService

router = APIRouter()


@router.get("", response_model=JobListResponse)
def list_jobs(
    current_user: CurrentUser,
    session: SessionDep,
    status_filter: Optional[JobStatus] = Query(default=None, alias="status"),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> JobListResponse:
    """List all jobs for the current user.

    Optional status filter and pagination support.
    """
    job_service = JobService(session)
    items, total = job_service.list_for_user(
        user_id=current_user.id,
        status=status_filter,
        limit=limit,
        offset=offset,
    )

    return JobListResponse(
        items=[JobListItem(**item) for item in items],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/{job_id}", response_model=JobStatusResponse)
def get_job_status(
    job_id: UUID,
    current_user: CurrentUser,
    session: SessionDep,
) -> JobStatusResponse:
    """Get the status of a processing job.

    Returns the current status of a job for polling.
    Only the owner of the job can retrieve its status.
    """
    job_service = JobService(session)
    job = job_service.get_job_for_user(job_id, current_user.id)

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )

    return JobStatusResponse(
        job_id=job.id,
        status=job.status,
        error_message=job.error_message,
        created_at=job.created_at,
        updated_at=job.updated_at,
    )
