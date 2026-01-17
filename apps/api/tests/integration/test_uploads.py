"""Integration tests for upload endpoints."""

from unittest.mock import MagicMock, patch
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
    """Create a test user for upload tests."""
    user = User(
        email="uploader@example.com",
        provider=AuthProvider.LOCAL,
        hashed_password=get_password_hash("testpassword123"),
        credits=10,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def other_user(db_session: Session) -> User:
    """Create another user for authorization tests."""
    user = User(
        email="other@example.com",
        provider=AuthProvider.LOCAL,
        hashed_password=get_password_hash("otherpassword"),
        credits=5,
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
def other_auth_headers(other_user: User) -> dict:
    """Create authorization headers for other user."""
    token = create_access_token(subject=str(other_user.id))
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def pending_job(db_session: Session, test_user: User) -> ProcessingJob:
    """Create a pending processing job."""
    job = ProcessingJob(
        user_id=test_user.id,
        s3_audio_key=f"uploads/{test_user.id}/{uuid4()}/test.mp3",
        status=JobStatus.PENDING,
    )
    db_session.add(job)
    db_session.commit()
    db_session.refresh(job)
    return job


class TestPresignedUrlEndpoint:
    """Tests for POST /api/v1/uploads/presigned-url."""

    @patch("app.api.v1.endpoints.uploads.S3ServiceDep")
    def test_generate_presigned_url_success(
        self, mock_s3_dep, client: TestClient, auth_headers: dict, db_session: Session
    ):
        """Successfully generate presigned URL and create job."""
        # Mock S3 service via dependency override
        mock_s3 = MagicMock()
        mock_s3.generate_presigned_upload_url.return_value = "https://s3.example.com/presigned"

        from app.api.deps import get_s3_service
        from app.main import app
        app.dependency_overrides[get_s3_service] = lambda: mock_s3

        try:
            response = client.post(
                "/api/v1/uploads/presigned-url",
                json={"filename": "interview.mp3", "content_type": "audio/mpeg"},
                headers=auth_headers,
            )

            assert response.status_code == 200
            data = response.json()
            assert "upload_url" in data
            assert "job_id" in data
            assert "s3_key" in data
            assert data["upload_url"] == "https://s3.example.com/presigned"
            assert "interview.mp3" in data["s3_key"]

            # Verify job was created in database
            job = db_session.get(ProcessingJob, data["job_id"])
            assert job is not None
            assert job.status == JobStatus.PENDING
            assert job.s3_audio_key == data["s3_key"]
        finally:
            app.dependency_overrides.pop(get_s3_service, None)

    def test_presigned_url_without_auth(self, client: TestClient):
        """Request without auth returns 401."""
        response = client.post(
            "/api/v1/uploads/presigned-url",
            json={"filename": "interview.mp3", "content_type": "audio/mpeg"},
        )

        assert response.status_code == 401
        assert response.json()["detail"] == "Not authenticated"

    def test_presigned_url_invalid_content_type(
        self, client: TestClient, auth_headers: dict
    ):
        """Invalid content type returns 422."""
        response = client.post(
            "/api/v1/uploads/presigned-url",
            json={"filename": "document.pdf", "content_type": "application/pdf"},
            headers=auth_headers,
        )

        assert response.status_code == 422

    def test_presigned_url_path_traversal_filename(
        self, client: TestClient, auth_headers: dict
    ):
        """Filename with path traversal returns 422."""
        response = client.post(
            "/api/v1/uploads/presigned-url",
            json={"filename": "../../../etc/passwd", "content_type": "audio/mpeg"},
            headers=auth_headers,
        )

        assert response.status_code == 422

    def test_presigned_url_empty_filename(
        self, client: TestClient, auth_headers: dict
    ):
        """Empty filename returns 422."""
        response = client.post(
            "/api/v1/uploads/presigned-url",
            json={"filename": "   ", "content_type": "audio/mpeg"},
            headers=auth_headers,
        )

        assert response.status_code == 422


class TestConfirmUploadEndpoint:
    """Tests for POST /api/v1/uploads/{job_id}/confirm."""

    def test_confirm_upload_success(
        self,
        client: TestClient,
        auth_headers: dict,
        pending_job: ProcessingJob,
        db_session: Session,
    ):
        """Successfully confirm upload updates status to QUEUED."""
        response = client.post(
            f"/api/v1/uploads/{pending_job.id}/confirm",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["job_id"] == str(pending_job.id)
        assert data["status"] == "queued"

        # Verify database was updated
        db_session.refresh(pending_job)
        assert pending_job.status == JobStatus.QUEUED

    def test_confirm_upload_not_found(
        self, client: TestClient, auth_headers: dict
    ):
        """Confirming non-existent job returns 404."""
        fake_id = uuid4()
        response = client.post(
            f"/api/v1/uploads/{fake_id}/confirm",
            headers=auth_headers,
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "Job not found"

    def test_confirm_upload_unauthorized(
        self,
        client: TestClient,
        other_auth_headers: dict,
        pending_job: ProcessingJob,
    ):
        """Confirming another user's job returns 403."""
        response = client.post(
            f"/api/v1/uploads/{pending_job.id}/confirm",
            headers=other_auth_headers,
        )

        assert response.status_code == 403
        assert response.json()["detail"] == "Not authorized"

    def test_confirm_upload_already_confirmed(
        self,
        client: TestClient,
        auth_headers: dict,
        pending_job: ProcessingJob,
        db_session: Session,
    ):
        """Confirming already confirmed job returns 400."""
        # First confirmation
        pending_job.status = JobStatus.QUEUED
        db_session.add(pending_job)
        db_session.commit()

        # Second confirmation attempt
        response = client.post(
            f"/api/v1/uploads/{pending_job.id}/confirm",
            headers=auth_headers,
        )

        assert response.status_code == 400
        assert response.json()["detail"] == "Job already confirmed"

    def test_confirm_upload_without_auth(
        self, client: TestClient, pending_job: ProcessingJob
    ):
        """Confirming without auth returns 401."""
        response = client.post(f"/api/v1/uploads/{pending_job.id}/confirm")

        assert response.status_code == 401
        assert response.json()["detail"] == "Not authenticated"
