"""Schemas for job status operations."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from app.models.enums import JobStatus


class JobStatusResponse(BaseModel):
    """Response schema for job status polling."""

    job_id: UUID
    status: JobStatus
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class JobListItem(BaseModel):
    """Single job item in list response."""

    job_id: UUID
    status: JobStatus
    interviewer_id: Optional[UUID] = None
    interviewer_name: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class JobListResponse(BaseModel):
    """Response schema for paginated job list."""

    items: list[JobListItem]
    total: int
    limit: int
    offset: int
