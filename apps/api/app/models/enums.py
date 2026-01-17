"""Enum definitions for database models."""

from enum import Enum


class AuthProvider(str, Enum):
    """OAuth authentication provider types."""

    GITHUB = "github"
    LINKEDIN = "linkedin"


class ProfileStatus(str, Enum):
    """Interviewer profile visibility status."""

    HIDDEN = "hidden"
    PUBLIC = "public"


class JobStatus(str, Enum):
    """Processing job status."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
