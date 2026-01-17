"""User schemas for request/response models."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr

from app.models.enums import AuthProvider


class UserCreate(BaseModel):
    """Schema for creating a local user account."""

    email: EmailStr
    password: str


class UserRead(BaseModel):
    """Safe user representation for API responses."""

    id: UUID
    email: str
    provider: AuthProvider
    credits: int
    created_at: datetime

    class Config:
        from_attributes = True
