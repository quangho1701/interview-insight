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
    user_id: UUID = Field(foreign_key="users.id", index=True)
    name: str = Field(index=True)
    email: Optional[str] = Field(default=None)
    company: Optional[str] = Field(default=None, index=True)
    profile_status: ProfileStatus = Field(default=ProfileStatus.HIDDEN)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
