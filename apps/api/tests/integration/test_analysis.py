"""Integration tests for analysis endpoints."""

from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.security import create_access_token, get_password_hash
from app.models.enums import AuthProvider, JobStatus
from app.models.interview_analysis import InterviewAnalysis
from app.models.interviewer import Interviewer
from app.models.processing_job import ProcessingJob
from app.models.user import User


@pytest.fixture
def test_user(db_session: Session) -> User:
    """Create a test user for analysis tests."""
    user = User(
        email="analysis_test@example.com",
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
        email="other_analysis@example.com",
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
def test_interviewer(db_session: Session, test_user: User) -> Interviewer:
    """Create a test interviewer."""
    interviewer = Interviewer(
        user_id=test_user.id,
        name="Test Interviewer",
        company="Test Company",
    )
    db_session.add(interviewer)
    db_session.commit()
    db_session.refresh(interviewer)
    return interviewer


@pytest.fixture
def completed_job_with_analysis(
    db_session: Session, test_user: User, test_interviewer: Interviewer
) -> tuple[ProcessingJob, InterviewAnalysis]:
    """Create a completed job with analysis."""
    # Create analysis first
    analysis = InterviewAnalysis(
        user_id=test_user.id,
        interviewer_id=test_interviewer.id,
        sentiment_score=0.75,
        summary="This was a positive interview with good technical discussion.",
        transcript_redacted="[REDACTED] discussed Python and FastAPI...",
        metrics_json={"keywords": ["python", "fastapi"], "duration_minutes": 45},
    )
    db_session.add(analysis)
    db_session.commit()
    db_session.refresh(analysis)

    # Create job referencing analysis
    job = ProcessingJob(
        user_id=test_user.id,
        interviewer_id=test_interviewer.id,
        analysis_id=analysis.id,
        s3_audio_key=f"uploads/{test_user.id}/interview.mp3",
        status=JobStatus.COMPLETED,
    )
    db_session.add(job)
    db_session.commit()
    db_session.refresh(job)

    return job, analysis


class TestGetAnalysis:
    """Tests for GET /api/v1/analysis/{job_id}."""

    def test_get_analysis_success(
        self,
        client: TestClient,
        auth_headers: dict,
        completed_job_with_analysis: tuple[ProcessingJob, InterviewAnalysis],
    ):
        """Successfully retrieve analysis for completed job."""
        job, analysis = completed_job_with_analysis

        response = client.get(
            f"/api/v1/analysis/{job.id}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["job_id"] == str(job.id)
        assert data["job_status"] == "completed"

        # Check analysis data
        assert data["analysis"]["id"] == str(analysis.id)
        assert data["analysis"]["sentiment_score"] == 0.75
        assert data["analysis"]["summary"] == "This was a positive interview with good technical discussion."
        assert data["analysis"]["transcript"] == "[REDACTED] discussed Python and FastAPI..."
        assert data["analysis"]["metrics"]["keywords"] == ["python", "fastapi"]
        assert data["analysis"]["metrics"]["duration_minutes"] == 45

        # Check interviewer data
        assert data["interviewer"]["name"] == "Test Interviewer"
        assert data["interviewer"]["company"] == "Test Company"

    def test_get_analysis_job_not_found(
        self, client: TestClient, auth_headers: dict
    ):
        """Request for non-existent job returns 404."""
        fake_id = uuid4()
        response = client.get(
            f"/api/v1/analysis/{fake_id}",
            headers=auth_headers,
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "Job not found"

    def test_get_analysis_job_pending(
        self,
        client: TestClient,
        auth_headers: dict,
        db_session: Session,
        test_user: User,
    ):
        """Request for pending job returns 400."""
        job = ProcessingJob(
            user_id=test_user.id,
            s3_audio_key=f"uploads/{test_user.id}/pending.mp3",
            status=JobStatus.PENDING,
        )
        db_session.add(job)
        db_session.commit()
        db_session.refresh(job)

        response = client.get(
            f"/api/v1/analysis/{job.id}",
            headers=auth_headers,
        )

        assert response.status_code == 400
        assert "not completed" in response.json()["detail"]
        assert "pending" in response.json()["detail"]

    def test_get_analysis_job_processing(
        self,
        client: TestClient,
        auth_headers: dict,
        db_session: Session,
        test_user: User,
    ):
        """Request for processing job returns 400."""
        job = ProcessingJob(
            user_id=test_user.id,
            s3_audio_key=f"uploads/{test_user.id}/processing.mp3",
            status=JobStatus.PROCESSING,
        )
        db_session.add(job)
        db_session.commit()
        db_session.refresh(job)

        response = client.get(
            f"/api/v1/analysis/{job.id}",
            headers=auth_headers,
        )

        assert response.status_code == 400
        assert "not completed" in response.json()["detail"]

    def test_get_analysis_job_failed(
        self,
        client: TestClient,
        auth_headers: dict,
        db_session: Session,
        test_user: User,
    ):
        """Request for failed job returns 400."""
        job = ProcessingJob(
            user_id=test_user.id,
            s3_audio_key=f"uploads/{test_user.id}/failed.mp3",
            status=JobStatus.FAILED,
            error_message="Transcription failed",
        )
        db_session.add(job)
        db_session.commit()
        db_session.refresh(job)

        response = client.get(
            f"/api/v1/analysis/{job.id}",
            headers=auth_headers,
        )

        assert response.status_code == 400
        assert "not completed" in response.json()["detail"]

    def test_get_analysis_completed_but_no_analysis(
        self,
        client: TestClient,
        auth_headers: dict,
        db_session: Session,
        test_user: User,
    ):
        """Completed job without analysis returns 404."""
        job = ProcessingJob(
            user_id=test_user.id,
            s3_audio_key=f"uploads/{test_user.id}/noanalysis.mp3",
            status=JobStatus.COMPLETED,
            analysis_id=None,  # No analysis linked
        )
        db_session.add(job)
        db_session.commit()
        db_session.refresh(job)

        response = client.get(
            f"/api/v1/analysis/{job.id}",
            headers=auth_headers,
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "Analysis not found for this job"

    def test_get_analysis_other_user(
        self,
        client: TestClient,
        other_auth_headers: dict,
        completed_job_with_analysis: tuple[ProcessingJob, InterviewAnalysis],
    ):
        """Cannot access another user's analysis - returns 404."""
        job, _ = completed_job_with_analysis

        response = client.get(
            f"/api/v1/analysis/{job.id}",
            headers=other_auth_headers,
        )

        # Returns 404 to avoid leaking existence information
        assert response.status_code == 404
        assert response.json()["detail"] == "Job not found"

    def test_get_analysis_without_auth(
        self,
        client: TestClient,
        completed_job_with_analysis: tuple[ProcessingJob, InterviewAnalysis],
    ):
        """Request without auth returns 401."""
        job, _ = completed_job_with_analysis

        response = client.get(f"/api/v1/analysis/{job.id}")

        assert response.status_code == 401
        assert response.json()["detail"] == "Not authenticated"

    def test_get_analysis_with_null_fields(
        self,
        client: TestClient,
        auth_headers: dict,
        db_session: Session,
        test_user: User,
        test_interviewer: Interviewer,
    ):
        """Analysis with null optional fields returns successfully."""
        # Create analysis with minimal data
        analysis = InterviewAnalysis(
            user_id=test_user.id,
            interviewer_id=test_interviewer.id,
            sentiment_score=0.0,
            summary=None,
            transcript_redacted=None,
            metrics_json=None,
        )
        db_session.add(analysis)
        db_session.commit()
        db_session.refresh(analysis)

        job = ProcessingJob(
            user_id=test_user.id,
            interviewer_id=test_interviewer.id,
            analysis_id=analysis.id,
            s3_audio_key=f"uploads/{test_user.id}/minimal.mp3",
            status=JobStatus.COMPLETED,
        )
        db_session.add(job)
        db_session.commit()
        db_session.refresh(job)

        response = client.get(
            f"/api/v1/analysis/{job.id}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["analysis"]["sentiment_score"] == 0.0
        assert data["analysis"]["summary"] is None
        assert data["analysis"]["transcript"] is None
        assert data["analysis"]["metrics"] is None
