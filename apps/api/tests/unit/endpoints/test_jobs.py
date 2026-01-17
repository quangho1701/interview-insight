"""Unit tests for jobs endpoint."""

from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.security import create_access_token, get_password_hash
from app.models.enums import AuthProvider, JobStatus
from app.models.processing_job import ProcessingJob
from app.models.user import User


@pytest.fixture
def test_user(db_session: Session) -> User:
    """Create a test user for job tests."""
    user = User(
        email="jobuser@example.com",
        provider=AuthProvider.LOCAL,
        hashed_password=get_password_hash("testpassword123"),
        credits=10,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def auth_headers(test_user: User) -> dict:
    """Create authorization headers for test user."""
    token = create_access_token(subject=str(test_user.id))
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def processing_job(db_session: Session, test_user: User) -> ProcessingJob:
    """Create a processing job in PROCESSING status."""
    job = ProcessingJob(
        user_id=test_user.id,
        s3_audio_key=f"uploads/{test_user.id}/interview.mp3",
        status=JobStatus.PROCESSING,
    )
    db_session.add(job)
    db_session.commit()
    db_session.refresh(job)
    return job


class TestGetJobStatus:
    """Tests for GET /api/v1/jobs/{job_id}."""

    def test_get_job_status_success(
        self,
        client: TestClient,
        auth_headers: dict,
        processing_job: ProcessingJob,
    ):
        """Successfully retrieve job status."""
        response = client.get(
            f"/api/v1/jobs/{processing_job.id}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["job_id"] == str(processing_job.id)
        assert data["status"] == "processing"
        assert data["error_message"] is None
        assert "created_at" in data
        assert "updated_at" in data

    def test_get_job_status_not_found(
        self, client: TestClient, auth_headers: dict
    ):
        """Request for non-existent job returns 404."""
        fake_id = uuid4()
        response = client.get(
            f"/api/v1/jobs/{fake_id}",
            headers=auth_headers,
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "Job not found"

    def test_get_job_status_unauthorized(
        self, client: TestClient, processing_job: ProcessingJob
    ):
        """Request without auth returns 401."""
        response = client.get(f"/api/v1/jobs/{processing_job.id}")

        assert response.status_code == 401
        assert response.json()["detail"] == "Not authenticated"

    def test_get_job_status_other_user(
        self,
        client: TestClient,
        db_session: Session,
        processing_job: ProcessingJob,
    ):
        """Request for another user's job returns 404."""
        # Create another user
        other_user = User(
            email="other@example.com",
            provider=AuthProvider.LOCAL,
            hashed_password=get_password_hash("otherpass"),
            credits=5,
        )
        db_session.add(other_user)
        db_session.commit()

        other_token = create_access_token(subject=str(other_user.id))
        other_headers = {"Authorization": f"Bearer {other_token}"}

        response = client.get(
            f"/api/v1/jobs/{processing_job.id}",
            headers=other_headers,
        )

        # Returns 404 (not 403) to avoid leaking job existence
        assert response.status_code == 404

    def test_get_job_with_error_message(
        self,
        client: TestClient,
        auth_headers: dict,
        db_session: Session,
        test_user: User,
    ):
        """Retrieve failed job includes error message."""
        failed_job = ProcessingJob(
            user_id=test_user.id,
            s3_audio_key=f"uploads/{test_user.id}/failed.mp3",
            status=JobStatus.FAILED,
            error_message="Transcription service unavailable",
        )
        db_session.add(failed_job)
        db_session.commit()
        db_session.refresh(failed_job)

        response = client.get(
            f"/api/v1/jobs/{failed_job.id}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "failed"
        assert data["error_message"] == "Transcription service unavailable"
