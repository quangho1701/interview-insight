"""Schemas for analysis retrieval operations."""

from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel

from app.models.enums import JobStatus
from app.schemas.interviewer import InterviewerRead


class AnalysisRead(BaseModel):
    """Response schema for interview analysis."""

    id: UUID
    sentiment_score: float
    summary: Optional[str] = None
    transcript: Optional[str] = None
    metrics: Optional[dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AnalysisWithJobResponse(BaseModel):
    """Response schema combining analysis with job metadata."""

    job_id: UUID
    job_status: JobStatus
    interviewer: InterviewerRead
    analysis: AnalysisRead

    class Config:
        from_attributes = True
