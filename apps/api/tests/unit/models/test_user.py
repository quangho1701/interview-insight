"""Unit tests for User model."""

from uuid import UUID

import pytest

from app.models.enums import AuthProvider
from app.models.user import User


class TestUserModel:
    """Tests for User SQLModel."""

    def test_user_model_creation(self):
        """User model creates with required fields."""
        user = User(
            provider=AuthProvider.GITHUB,
            email="test@example.com",
        )

        assert user.provider == AuthProvider.GITHUB
        assert user.email == "test@example.com"
        assert isinstance(user.id, UUID)  # UUID auto-generated

    def test_user_model_credits_default(self):
        """User has default credits = 0."""
        user = User(
            provider=AuthProvider.GITHUB,
            email="test@example.com",
        )

        assert user.credits == 0

    def test_user_model_provider_enum(self):
        """Only GITHUB/LINKEDIN values accepted for provider."""
        # Valid providers
        github_user = User(provider=AuthProvider.GITHUB, email="gh@test.com")
        linkedin_user = User(provider=AuthProvider.LINKEDIN, email="li@test.com")

        assert github_user.provider == AuthProvider.GITHUB
        assert linkedin_user.provider == AuthProvider.LINKEDIN

        # Verify enum values exist
        assert AuthProvider.GITHUB.value == "github"
        assert AuthProvider.LINKEDIN.value == "linkedin"
