"""Service for interviewer operations."""

from typing import Optional
from uuid import UUID

from sqlmodel import Session, func, select

from app.models.interviewer import Interviewer
from app.schemas.interviewer import InterviewerCreate


class InterviewerService:
    """Service for interviewer-related operations."""

    def __init__(self, session: Session):
        """Initialize with database session."""
        self.session = session

    def create(self, user_id: UUID, data: InterviewerCreate) -> Interviewer:
        """Create a new interviewer for a user.

        Args:
            user_id: UUID of the owning user.
            data: Interviewer creation data.

        Returns:
            The created Interviewer instance.
        """
        interviewer = Interviewer(
            user_id=user_id,
            name=data.name,
            company=data.company,
            email=data.email,
        )
        self.session.add(interviewer)
        self.session.commit()
        self.session.refresh(interviewer)
        return interviewer

    def get_by_id(
        self, interviewer_id: UUID, user_id: UUID
    ) -> Optional[Interviewer]:
        """Get interviewer by ID, verifying user ownership.

        Args:
            interviewer_id: UUID of the interviewer to retrieve.
            user_id: UUID of the requesting user.

        Returns:
            Interviewer if found and owned by user, None otherwise.
        """
        stmt = select(Interviewer).where(
            Interviewer.id == interviewer_id,
            Interviewer.user_id == user_id,
        )
        return self.session.exec(stmt).first()

    def list_for_user(
        self, user_id: UUID, limit: int = 50, offset: int = 0
    ) -> tuple[list[Interviewer], int]:
        """List interviewers for a user with pagination.

        Args:
            user_id: UUID of the user.
            limit: Maximum number of items to return.
            offset: Number of items to skip.

        Returns:
            Tuple of (list of interviewers, total count).
        """
        # Count total
        count_stmt = (
            select(func.count())
            .select_from(Interviewer)
            .where(Interviewer.user_id == user_id)
        )
        total = self.session.exec(count_stmt).one()

        # Fetch items
        stmt = (
            select(Interviewer)
            .where(Interviewer.user_id == user_id)
            .order_by(Interviewer.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        items = list(self.session.exec(stmt).all())

        return items, total
