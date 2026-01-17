"""Unit tests for JobService."""

from uuid import uuid4

import pytest
from sqlmodel import Session

from app.models.enums import AuthProvider, JobStatus
from app.models.processing_job import ProcessingJob
from app.models.user import User
from app.services.job_service import JobService


@pytest.fixture
def test_user(db_session: Session) -> User:
    """Create a test user."""
    user = User(
        email="jobtest@example.com",
        provider=AuthProvider.LOCAL,
        hashed_password="hashedpassword",
        credits=10,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_job(db_session: Session, test_user: User) -> ProcessingJob:
    """Create a test processing job."""
    job = ProcessingJob(
        user_id=test_user.id,
        s3_audio_key=f"uploads/{test_user.id}/test.mp3",
        status=JobStatus.QUEUED,
    )
    db_session.add(job)
    db_session.commit()
    db_session.refresh(job)
    return job


class TestJobService:
    """Tests for JobService."""

    def test_get_job_found(
        self, db_session: Session, test_job: ProcessingJob
    ):
        """get_job returns job when found."""
        service = JobService(db_session)
        result = service.get_job(test_job.id)

        assert result is not None
        assert result.id == test_job.id
        assert result.status == JobStatus.QUEUED

    def test_get_job_not_found(self, db_session: Session):
        """get_job returns None for non-existent job."""
        service = JobService(db_session)
        result = service.get_job(uuid4())

        assert result is None

    def test_get_job_for_user_owner(
        self, db_session: Session, test_job: ProcessingJob, test_user: User
    ):
        """get_job_for_user returns job when user is owner."""
        service = JobService(db_session)
        result = service.get_job_for_user(test_job.id, test_user.id)

        assert result is not None
        assert result.id == test_job.id

    def test_get_job_for_user_not_owner(
        self, db_session: Session, test_job: ProcessingJob
    ):
        """get_job_for_user returns None when user is not owner."""
        service = JobService(db_session)
        other_user_id = uuid4()
        result = service.get_job_for_user(test_job.id, other_user_id)

        assert result is None

    def test_get_job_for_user_not_found(
        self, db_session: Session, test_user: User
    ):
        """get_job_for_user returns None for non-existent job."""
        service = JobService(db_session)
        result = service.get_job_for_user(uuid4(), test_user.id)

        assert result is None
