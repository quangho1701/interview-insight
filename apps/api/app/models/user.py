"""User model definition."""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel

from app.models.enums import AuthProvider


class User(SQLModel, table=True):
    """User model representing authenticated users."""

    __tablename__ = "users"

    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    provider: AuthProvider = Field(index=True)
    email: str = Field(index=True, unique=True)
    credits: int = Field(default=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
