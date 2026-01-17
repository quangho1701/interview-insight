"""Interviewer model definition."""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel

from app.models.enums import ProfileStatus


class Interviewer(SQLModel, table=True):
    """Interviewer model representing interview conductors."""

    __tablename__ = "interviewers"

    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(index=True)
    company: str = Field(index=True)
    profile_status: ProfileStatus = Field(default=ProfileStatus.HIDDEN)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
