"""Enum definitions for database models."""

from enum import Enum


class AuthProvider(str, Enum):
    """Authentication provider types."""

    LOCAL = "local"
    GITHUB = "github"
    LINKEDIN = "linkedin"
    CLERK = "clerk"


class ProfileStatus(str, Enum):
    """Interviewer profile visibility status."""

    HIDDEN = "hidden"
    PUBLIC = "public"


class JobStatus(str, Enum):
    """Processing job status."""

    PENDING = "pending"
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
