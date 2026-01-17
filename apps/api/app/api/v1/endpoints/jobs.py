"""Job status endpoints."""

from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from app.api.deps import CurrentUser, SessionDep
from app.schemas.job import JobStatusResponse
from app.services.job_service import JobService

router = APIRouter()


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
