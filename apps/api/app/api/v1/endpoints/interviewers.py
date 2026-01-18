"""Interviewer management endpoints."""

from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status

from app.api.deps import CurrentUser, SessionDep
from app.schemas.interviewer import (
    InterviewerCreate,
    InterviewerListResponse,
    InterviewerRead,
)
from app.services.interviewer_service import InterviewerService

router = APIRouter()


@router.post("", response_model=InterviewerRead, status_code=status.HTTP_201_CREATED)
def create_interviewer(
    data: InterviewerCreate,
    current_user: CurrentUser,
    session: SessionDep,
) -> InterviewerRead:
    """Create a new interviewer.

    Creates an interviewer associated with the current user.
    """
    service = InterviewerService(session)
    interviewer = service.create(user_id=current_user.id, data=data)
    return InterviewerRead.model_validate(interviewer)


@router.get("", response_model=InterviewerListResponse)
def list_interviewers(
    current_user: CurrentUser,
    session: SessionDep,
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> InterviewerListResponse:
    """List all interviewers for the current user.

    Returns paginated list of interviewers.
    """
    service = InterviewerService(session)
    items, total = service.list_for_user(
        user_id=current_user.id,
        limit=limit,
        offset=offset,
    )
    return InterviewerListResponse(
        items=[InterviewerRead.model_validate(i) for i in items],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/{interviewer_id}", response_model=InterviewerRead)
def get_interviewer(
    interviewer_id: UUID,
    current_user: CurrentUser,
    session: SessionDep,
) -> InterviewerRead:
    """Get a specific interviewer by ID.

    Only returns interviewer if owned by current user.
    """
    service = InterviewerService(session)
    interviewer = service.get_by_id(
        interviewer_id=interviewer_id,
        user_id=current_user.id,
    )

    if not interviewer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interviewer not found",
        )

    return InterviewerRead.model_validate(interviewer)
