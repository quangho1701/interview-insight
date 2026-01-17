"""Upload endpoints for S3 presigned URL generation."""

from uuid import UUID, uuid4

from botocore.exceptions import ClientError
from fastapi import APIRouter, HTTPException, status

from app.api.deps import CurrentUser, S3ServiceDep, SessionDep
from app.core.celery_utils import enqueue_interview_processing
from app.models.enums import JobStatus
from app.models.processing_job import ProcessingJob
from app.schemas.upload import (
    JobConfirmResponse,
    PresignedUrlRequest,
    PresignedUrlResponse,
)

router = APIRouter()


@router.post("/presigned-url", response_model=PresignedUrlResponse)
def create_presigned_url(
    request: PresignedUrlRequest,
    current_user: CurrentUser,
    session: SessionDep,
    s3_service: S3ServiceDep,
) -> PresignedUrlResponse:
    """Generate a presigned URL for file upload.

    Creates a ProcessingJob record and returns a presigned S3 URL
    that the client can use to upload the file directly to S3.
    """
    # Generate unique S3 key
    s3_key = f"uploads/{current_user.id}/{uuid4()}/{request.filename}"

    # Create processing job record
    job = ProcessingJob(
        user_id=current_user.id,
        s3_audio_key=s3_key,
        status=JobStatus.PENDING,
    )
    session.add(job)
    session.commit()
    session.refresh(job)

    # Generate presigned URL
    try:
        upload_url = s3_service.generate_presigned_upload_url(
            object_key=s3_key,
            content_type=request.content_type,
        )
    except ClientError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="S3 service unavailable",
        )

    return PresignedUrlResponse(
        upload_url=upload_url,
        job_id=job.id,
        s3_key=s3_key,
    )


@router.post("/{job_id}/confirm", response_model=JobConfirmResponse)
def confirm_upload(
    job_id: UUID,
    current_user: CurrentUser,
    session: SessionDep,
) -> JobConfirmResponse:
    """Confirm that a file upload has completed.

    Updates the ProcessingJob status from PENDING to QUEUED,
    marking it ready for processing.
    """
    job = session.get(ProcessingJob, job_id)

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )

    if job.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized",
        )

    if job.status != JobStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Job already confirmed",
        )

    job.status = JobStatus.QUEUED
    session.add(job)
    session.commit()
    session.refresh(job)

    # Trigger Celery task for async processing
    enqueue_interview_processing(str(job.id))

    return JobConfirmResponse(job_id=job.id, status=job.status)
