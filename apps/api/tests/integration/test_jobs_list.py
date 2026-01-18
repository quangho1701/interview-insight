"""Integration tests for job list endpoint."""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.security import create_access_token, get_password_hash
from app.models.enums import AuthProvider, JobStatus
from app.models.interviewer import Interviewer
from app.models.processing_job import ProcessingJob
from app.models.user import User


@pytest.fixture
def test_user(db_session: Session) -> User:
    """Create a test user."""
    user = User(
        email="jobs_list@example.com",
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
        email="other_jobs@example.com",
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
    """Create authorization headers."""
    token = create_access_token(subject=str(test_user.id))
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def other_auth_headers(other_user: User) -> dict:
    """Create authorization headers for other user."""
    token = create_access_token(subject=str(other_user.id))
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def test_interviewer(db_session: Session, test_user: User) -> Interviewer:
    """Create a test interviewer."""
    interviewer = Interviewer(
        user_id=test_user.id,
        name="List Test Interviewer",
        company="Test Co",
    )
    db_session.add(interviewer)
    db_session.commit()
    db_session.refresh(interviewer)
    return interviewer


@pytest.fixture
def jobs_with_interviewers(
    db_session: Session, test_user: User, test_interviewer: Interviewer
) -> list[ProcessingJob]:
    """Create multiple jobs with varying statuses."""
    jobs = []
    statuses = [
        JobStatus.PENDING,
        JobStatus.QUEUED,
        JobStatus.PROCESSING,
        JobStatus.COMPLETED,
        JobStatus.FAILED,
    ]

    for i, status in enumerate(statuses):
        job = ProcessingJob(
            user_id=test_user.id,
            interviewer_id=test_interviewer.id if i > 0 else None,
            s3_audio_key=f"uploads/{test_user.id}/file_{i}.mp3",
            status=status,
            error_message="Test error" if status == JobStatus.FAILED else None,
        )
        db_session.add(job)
        jobs.append(job)

    db_session.commit()
    for job in jobs:
        db_session.refresh(job)

    return jobs


class TestListJobs:
    """Tests for GET /api/v1/jobs."""

    def test_list_jobs_success(
        self, client: TestClient, auth_headers: dict, jobs_with_interviewers: list
    ):
        """Successfully list all jobs."""
        response = client.get("/api/v1/jobs", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 5
        assert len(data["items"]) == 5
        assert "limit" in data
        assert "offset" in data

    def test_list_jobs_empty(self, client: TestClient, auth_headers: dict):
        """List returns empty when no jobs exist."""
        response = client.get("/api/v1/jobs", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["items"] == []

    def test_list_jobs_filter_by_status_completed(
        self, client: TestClient, auth_headers: dict, jobs_with_interviewers: list
    ):
        """Filter jobs by completed status."""
        response = client.get(
            "/api/v1/jobs?status=completed",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert len(data["items"]) == 1
        assert data["items"][0]["status"] == "completed"

    def test_list_jobs_filter_by_status_failed(
        self, client: TestClient, auth_headers: dict, jobs_with_interviewers: list
    ):
        """Filter jobs by failed status."""
        response = client.get(
            "/api/v1/jobs?status=failed",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["status"] == "failed"
        assert data["items"][0]["error_message"] == "Test error"

    def test_list_jobs_filter_by_status_pending(
        self, client: TestClient, auth_headers: dict, jobs_with_interviewers: list
    ):
        """Filter jobs by pending status."""
        response = client.get(
            "/api/v1/jobs?status=pending",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["status"] == "pending"

    def test_list_jobs_pagination(
        self, client: TestClient, auth_headers: dict, jobs_with_interviewers: list
    ):
        """Test pagination with limit."""
        response = client.get(
            "/api/v1/jobs?limit=2&offset=0",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2
        assert data["total"] == 5
        assert data["limit"] == 2
        assert data["offset"] == 0

    def test_list_jobs_pagination_offset(
        self, client: TestClient, auth_headers: dict, jobs_with_interviewers: list
    ):
        """Test pagination with offset."""
        response = client.get(
            "/api/v1/jobs?limit=2&offset=3",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2
        assert data["total"] == 5
        assert data["offset"] == 3

    def test_list_jobs_includes_interviewer_name(
        self, client: TestClient, auth_headers: dict, jobs_with_interviewers: list
    ):
        """Jobs include interviewer name when available."""
        response = client.get("/api/v1/jobs", headers=auth_headers)

        data = response.json()
        # Find jobs that have an interviewer (all except the first one)
        jobs_with_name = [j for j in data["items"] if j["interviewer_name"]]
        assert len(jobs_with_name) == 4  # 4 jobs have interviewer_id
        assert jobs_with_name[0]["interviewer_name"] == "List Test Interviewer"

    def test_list_jobs_job_without_interviewer(
        self, client: TestClient, auth_headers: dict, jobs_with_interviewers: list
    ):
        """Jobs without interviewer have null interviewer fields."""
        response = client.get("/api/v1/jobs", headers=auth_headers)

        data = response.json()
        # Find the pending job which has no interviewer
        jobs_without_interviewer = [
            j for j in data["items"] if j["interviewer_id"] is None
        ]
        assert len(jobs_without_interviewer) == 1
        assert jobs_without_interviewer[0]["interviewer_name"] is None
        assert jobs_without_interviewer[0]["status"] == "pending"

    def test_list_jobs_user_isolation(
        self,
        client: TestClient,
        auth_headers: dict,
        other_auth_headers: dict,
        jobs_with_interviewers: list,
        other_user: User,
        db_session: Session,
    ):
        """User cannot see other user's jobs."""
        # Create a job for other user
        other_job = ProcessingJob(
            user_id=other_user.id,
            s3_audio_key=f"uploads/{other_user.id}/other.mp3",
            status=JobStatus.PENDING,
        )
        db_session.add(other_job)
        db_session.commit()

        # Get jobs for other user
        response = client.get("/api/v1/jobs", headers=other_auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        # Should only see their own job
        assert data["items"][0]["status"] == "pending"

    def test_list_jobs_without_auth(self, client: TestClient):
        """Request without auth returns 401."""
        response = client.get("/api/v1/jobs")

        assert response.status_code == 401
        assert response.json()["detail"] == "Not authenticated"

    def test_list_jobs_ordered_by_created_at_desc(
        self, client: TestClient, auth_headers: dict, jobs_with_interviewers: list
    ):
        """Jobs are ordered by created_at descending (newest first)."""
        response = client.get("/api/v1/jobs", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        # Verify ordering by comparing created_at timestamps
        items = data["items"]
        for i in range(len(items) - 1):
            assert items[i]["created_at"] >= items[i + 1]["created_at"]

    def test_list_jobs_invalid_status_filter(
        self, client: TestClient, auth_headers: dict
    ):
        """Invalid status filter returns 422."""
        response = client.get(
            "/api/v1/jobs?status=invalid_status",
            headers=auth_headers,
        )

        assert response.status_code == 422

    def test_list_jobs_combined_filter_and_pagination(
        self,
        client: TestClient,
        auth_headers: dict,
        db_session: Session,
        test_user: User,
    ):
        """Test combining status filter with pagination."""
        # Create 5 completed jobs
        for i in range(5):
            job = ProcessingJob(
                user_id=test_user.id,
                s3_audio_key=f"uploads/{test_user.id}/completed_{i}.mp3",
                status=JobStatus.COMPLETED,
            )
            db_session.add(job)
        db_session.commit()

        response = client.get(
            "/api/v1/jobs?status=completed&limit=2&offset=1",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 5
        assert len(data["items"]) == 2
        assert all(item["status"] == "completed" for item in data["items"])
