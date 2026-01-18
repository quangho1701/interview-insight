"""ProcessingJob model definition."""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel

from app.models.enums import JobStatus


class ProcessingJob(SQLModel, table=True):
    """ProcessingJob model representing async analysis jobs."""

    __tablename__ = "processing_jobs"

    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    interviewer_id: Optional[UUID] = Field(
        default=None,
        foreign_key="interviewers.id",
        index=True,
    )
    analysis_id: Optional[UUID] = Field(
        default=None,
        foreign_key="interview_analyses.id",
    )
    s3_audio_key: str = Field()
    status: JobStatus = Field(default=JobStatus.PENDING, index=True)
    error_message: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
