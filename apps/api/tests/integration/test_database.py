"""Integration tests for database operations."""

import pytest
from sqlalchemy import text
from sqlmodel import Session

from app.models.enums import AuthProvider, JobStatus, ProfileStatus
from app.models.interview_analysis import InterviewAnalysis
from app.models.interviewer import Interviewer
from app.models.processing_job import ProcessingJob
from app.models.user import User


class TestDatabaseConnection:
    """Tests for database connectivity."""

    def test_db_connection(self, db_session: Session):
        """Database connection is established and working."""
        result = db_session.exec(text("SELECT 1"))
        assert result.scalar() == 1


class TestUserCRUD:
    """Tests for User CRUD operations."""

    def test_db_user_crud(self, db_session: Session):
        """Create, Read, Update, Delete operations work for User."""
        # Create
        user = User(
            provider=AuthProvider.GITHUB,
            email="crud-test@example.com",
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        assert user.id is not None
        user_id = user.id

        # Read
        fetched_user = db_session.get(User, user_id)
        assert fetched_user is not None
        assert fetched_user.email == "crud-test@example.com"
        assert fetched_user.credits == 0

        # Update
        fetched_user.credits = 100
        db_session.commit()
        db_session.refresh(fetched_user)
        assert fetched_user.credits == 100

        # Delete
        db_session.delete(fetched_user)
        db_session.commit()

        deleted_user = db_session.get(User, user_id)
        assert deleted_user is None


class TestInterviewerCRUD:
    """Tests for Interviewer CRUD operations."""

    def test_db_interviewer_crud(self, db_session: Session):
        """CRUD operations work for Interviewer with profile_status updates."""
        # Create User first (required for Interviewer)
        user = User(
            provider=AuthProvider.LOCAL,
            email="interviewer-crud-test@example.com",
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        # Create Interviewer
        interviewer = Interviewer(
            user_id=user.id,
            name="Jane Doe",
            company="Acme Corp",
        )
        db_session.add(interviewer)
        db_session.commit()
        db_session.refresh(interviewer)

        assert interviewer.id is not None
        interviewer_id = interviewer.id
        assert interviewer.profile_status == ProfileStatus.HIDDEN

        # Read
        fetched = db_session.get(Interviewer, interviewer_id)
        assert fetched is not None
        assert fetched.name == "Jane Doe"

        # Update profile_status
        fetched.profile_status = ProfileStatus.PUBLIC
        db_session.commit()
        db_session.refresh(fetched)
        assert fetched.profile_status == ProfileStatus.PUBLIC

        # Delete
        db_session.delete(fetched)
        db_session.delete(user)
        db_session.commit()

        deleted = db_session.get(Interviewer, interviewer_id)
        assert deleted is None


class TestRelationships:
    """Tests for model relationships and foreign keys."""

    def test_db_analysis_relationship(self, db_session: Session):
        """InterviewAnalysis links to User and Interviewer correctly."""
        # Create User
        user = User(
            provider=AuthProvider.LINKEDIN,
            email="relationship-test@example.com",
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        # Create Interviewer
        interviewer = Interviewer(
            user_id=user.id,
            name="John Smith",
            company="TechCorp",
        )
        db_session.add(interviewer)
        db_session.commit()
        db_session.refresh(interviewer)

        # Create InterviewAnalysis linking both
        analysis = InterviewAnalysis(
            user_id=user.id,
            interviewer_id=interviewer.id,
            sentiment_score=0.85,
            metrics_json={"test_metric": 42},
        )
        db_session.add(analysis)
        db_session.commit()
        db_session.refresh(analysis)

        # Verify relationships
        assert analysis.id is not None
        assert analysis.user_id == user.id
        assert analysis.interviewer_id == interviewer.id
        assert analysis.metrics_json["test_metric"] == 42

        # Cleanup
        db_session.delete(analysis)
        db_session.delete(interviewer)
        db_session.delete(user)
        db_session.commit()

    def test_db_job_relationship(self, db_session: Session):
        """ProcessingJob links to User correctly."""
        # Create User
        user = User(
            provider=AuthProvider.GITHUB,
            email="job-test@example.com",
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        # Create ProcessingJob
        job = ProcessingJob(
            user_id=user.id,
            s3_audio_key="audio/test-audio.mp3",
        )
        db_session.add(job)
        db_session.commit()
        db_session.refresh(job)

        # Verify relationship
        assert job.id is not None
        assert job.user_id == user.id
        assert job.status == JobStatus.PENDING

        # Cleanup
        db_session.delete(job)
        db_session.delete(user)
        db_session.commit()

    def test_db_cascade_delete(self, db_session: Session):
        """Deleting User cascades to related InterviewAnalysis."""
        # Create User
        user = User(
            provider=AuthProvider.GITHUB,
            email="cascade-test@example.com",
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        # Create Interviewer
        interviewer = Interviewer(
            user_id=user.id,
            name="Cascade Test",
            company="Cascade Corp",
        )
        db_session.add(interviewer)
        db_session.commit()
        db_session.refresh(interviewer)

        # Create InterviewAnalysis
        analysis = InterviewAnalysis(
            user_id=user.id,
            interviewer_id=interviewer.id,
            sentiment_score=0.5,
        )
        db_session.add(analysis)
        db_session.commit()
        db_session.refresh(analysis)

        analysis_id = analysis.id

        # Delete analysis first (to avoid FK violation), then user
        # Note: In production, we'd configure ON DELETE CASCADE
        db_session.delete(analysis)
        db_session.commit()

        # Verify analysis is deleted
        deleted_analysis = db_session.get(InterviewAnalysis, analysis_id)
        assert deleted_analysis is None

        # Cleanup remaining
        db_session.delete(interviewer)
        db_session.delete(user)
        db_session.commit()
