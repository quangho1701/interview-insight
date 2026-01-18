"""InterviewAnalysis model definition."""

from datetime import datetime
from typing import Any, Optional
from uuid import UUID, uuid4

from sqlmodel import Column, Field, SQLModel
from sqlalchemy.dialects.postgresql import JSONB


class InterviewAnalysis(SQLModel, table=True):
    """InterviewAnalysis model representing analyzed interview data."""

    __tablename__ = "interview_analyses"

    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    interviewer_id: UUID = Field(foreign_key="interviewers.id", index=True)
    sentiment_score: float = Field(ge=-1.0, le=1.0)
    summary: Optional[str] = Field(default=None)
    metrics_json: Optional[dict[str, Any]] = Field(
        default=None,
        sa_column=Column(JSONB),
    )
    transcript_redacted: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
