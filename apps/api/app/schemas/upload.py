"""Schemas for file upload operations."""

from uuid import UUID

from pydantic import BaseModel, field_validator

from app.models.enums import JobStatus
from app.services.s3_service import ALLOWED_CONTENT_TYPES


class PresignedUrlRequest(BaseModel):
    """Request schema for generating a presigned upload URL."""

    filename: str
    content_type: str

    @field_validator("content_type")
    @classmethod
    def validate_content_type(cls, v: str) -> str:
        """Validate that content type is an allowed audio type."""
        if v not in ALLOWED_CONTENT_TYPES:
            raise ValueError(f"Content type must be one of: {ALLOWED_CONTENT_TYPES}")
        return v

    @field_validator("filename")
    @classmethod
    def validate_filename(cls, v: str) -> str:
        """Validate filename to prevent path traversal attacks."""
        if ".." in v or "/" in v or "\\" in v:
            raise ValueError("Invalid filename")
        if not v.strip():
            raise ValueError("Filename cannot be empty")
        return v


class PresignedUrlResponse(BaseModel):
    """Response schema for presigned upload URL."""

    upload_url: str
    job_id: UUID
    s3_key: str


class JobConfirmResponse(BaseModel):
    """Response schema for job confirmation."""

    job_id: UUID
    status: JobStatus
