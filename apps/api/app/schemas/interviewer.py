"""Schemas for interviewer operations."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from app.models.enums import ProfileStatus


class InterviewerCreate(BaseModel):
    """Request schema for creating an interviewer."""

    name: str = Field(..., min_length=1, max_length=255)
    company: str = Field(..., min_length=1, max_length=255)
    email: Optional[EmailStr] = None


class InterviewerRead(BaseModel):
    """Response schema for interviewer data."""

    id: UUID
    name: str
    company: str
    email: Optional[str] = None
    profile_status: ProfileStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class InterviewerListResponse(BaseModel):
    """Response schema for paginated interviewer list."""

    items: list[InterviewerRead]
    total: int
    limit: int
    offset: int
