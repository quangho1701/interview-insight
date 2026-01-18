"""User schemas for request/response models."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from app.models.enums import AuthProvider


class UserCreate(BaseModel):
    """Schema for creating a local user account."""

    email: EmailStr
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters")
    full_name: Optional[str] = Field(default=None, max_length=255)


class UserRead(BaseModel):
    """Safe user representation for API responses."""

    id: UUID
    email: str
    provider: AuthProvider
    credits: int
    created_at: datetime

    class Config:
        from_attributes = True
