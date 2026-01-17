"""Unit tests for Interviewer model."""

from uuid import UUID

import pytest

from app.models.enums import ProfileStatus
from app.models.interviewer import Interviewer


class TestInterviewerModel:
    """Tests for Interviewer SQLModel."""

    def test_interviewer_model_creation(self):
        """Interviewer model creates with name and company."""
        interviewer = Interviewer(
            name="Jane Doe",
            company="Acme Corp",
        )

        assert interviewer.name == "Jane Doe"
        assert interviewer.company == "Acme Corp"
        assert isinstance(interviewer.id, UUID)  # UUID auto-generated

    def test_interviewer_profile_status_enum(self):
        """Only HIDDEN/PUBLIC values accepted for profile_status."""
        # Verify enum values exist
        assert ProfileStatus.HIDDEN.value == "hidden"
        assert ProfileStatus.PUBLIC.value == "public"

        # Create interviewer with explicit status
        hidden_interviewer = Interviewer(
            name="Test",
            company="Test Co",
            profile_status=ProfileStatus.HIDDEN,
        )
        public_interviewer = Interviewer(
            name="Test2",
            company="Test Co",
            profile_status=ProfileStatus.PUBLIC,
        )

        assert hidden_interviewer.profile_status == ProfileStatus.HIDDEN
        assert public_interviewer.profile_status == ProfileStatus.PUBLIC

    def test_interviewer_profile_status_default(self):
        """New interviewer starts as HIDDEN."""
        interviewer = Interviewer(
            name="Jane Doe",
            company="Acme Corp",
        )

        assert interviewer.profile_status == ProfileStatus.HIDDEN
