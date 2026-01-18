"""Analysis retrieval endpoints."""

from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from app.api.deps import CurrentUser, SessionDep
from app.models.enums import JobStatus
from app.models.interview_analysis import InterviewAnalysis
from app.models.interviewer import Interviewer
from app.schemas.analysis import AnalysisRead, AnalysisWithJobResponse
from app.schemas.interviewer import InterviewerRead
from app.services.job_service import JobService

router = APIRouter()


@router.get("/{job_id}", response_model=AnalysisWithJobResponse)
def get_analysis(
    job_id: UUID,
    current_user: CurrentUser,
    session: SessionDep,
) -> AnalysisWithJobResponse:
    """Get analysis results for a completed job.

    Verifies job ownership and completion status before returning analysis.
    Returns 404 if job not found or not owned by user.
    Returns 400 if job is not yet completed.
    """
    job_service = JobService(session)
    job = job_service.get_job_for_user(job_id=job_id, user_id=current_user.id)

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )

    if job.status != JobStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Job is not completed. Current status: {job.status.value}",
        )

    if not job.analysis_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found for this job",
        )

    # Fetch analysis
    analysis = session.get(InterviewAnalysis, job.analysis_id)
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found",
        )

    # Fetch interviewer
    interviewer = session.get(Interviewer, job.interviewer_id)
    if not interviewer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interviewer not found",
        )

    return AnalysisWithJobResponse(
        job_id=job.id,
        job_status=job.status,
        interviewer=InterviewerRead.model_validate(interviewer),
        analysis=AnalysisRead(
            id=analysis.id,
            sentiment_score=analysis.sentiment_score,
            summary=analysis.summary,
            transcript=analysis.transcript_redacted,
            metrics=analysis.metrics_json,
            created_at=analysis.created_at,
            updated_at=analysis.updated_at,
        ),
    )
