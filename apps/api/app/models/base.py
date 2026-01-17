"""Base model with common fields."""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class TimestampMixin(SQLModel):
    """Mixin that adds created_at and updated_at timestamps."""

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class UUIDMixin(SQLModel):
    """Mixin that adds UUID primary key."""

    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
