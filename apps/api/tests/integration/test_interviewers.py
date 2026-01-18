"""Integration tests for interviewer endpoints."""

from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.security import create_access_token, get_password_hash
from app.models.enums import AuthProvider, ProfileStatus
from app.models.interviewer import Interviewer
from app.models.user import User


@pytest.fixture
def test_user(db_session: Session) -> User:
    """Create a test user for interviewer tests."""
    user = User(
        email="interviewer_test@example.com",
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
        email="other_interviewer@example.com",
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
        name="John Doe",
        company="TechCorp",
        email="john.doe@techcorp.com",
    )
    db_session.add(interviewer)
    db_session.commit()
    db_session.refresh(interviewer)
    return interviewer


class TestCreateInterviewer:
    """Tests for POST /api/v1/interviewers."""

    def test_create_interviewer_success(
        self, client: TestClient, auth_headers: dict, db_session: Session
    ):
        """Successfully create an interviewer."""
        response = client.post(
            "/api/v1/interviewers",
            json={"name": "Jane Smith", "company": "StartupXYZ"},
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Jane Smith"
        assert data["company"] == "StartupXYZ"
        assert data["email"] is None
        assert data["profile_status"] == "hidden"
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data

    def test_create_interviewer_with_email(
        self, client: TestClient, auth_headers: dict
    ):
        """Create interviewer with optional email."""
        response = client.post(
            "/api/v1/interviewers",
            json={
                "name": "Bob Johnson",
                "company": "BigCo",
                "email": "bob@bigco.com",
            },
            headers=auth_headers,
        )

        assert response.status_code == 201
        assert response.json()["email"] == "bob@bigco.com"

    def test_create_interviewer_without_auth(self, client: TestClient):
        """Request without auth returns 401."""
        response = client.post(
            "/api/v1/interviewers",
            json={"name": "Test", "company": "Test"},
        )

        assert response.status_code == 401
        assert response.json()["detail"] == "Not authenticated"

    def test_create_interviewer_missing_name(
        self, client: TestClient, auth_headers: dict
    ):
        """Request without name returns 422."""
        response = client.post(
            "/api/v1/interviewers",
            json={"company": "TestCo"},
            headers=auth_headers,
        )

        assert response.status_code == 422

    def test_create_interviewer_missing_company(
        self, client: TestClient, auth_headers: dict
    ):
        """Request without company returns 422."""
        response = client.post(
            "/api/v1/interviewers",
            json={"name": "Test Name"},
            headers=auth_headers,
        )

        assert response.status_code == 422

    def test_create_interviewer_invalid_email(
        self, client: TestClient, auth_headers: dict
    ):
        """Request with invalid email returns 422."""
        response = client.post(
            "/api/v1/interviewers",
            json={"name": "Test", "company": "TestCo", "email": "not-an-email"},
            headers=auth_headers,
        )

        assert response.status_code == 422


class TestListInterviewers:
    """Tests for GET /api/v1/interviewers."""

    def test_list_interviewers_success(
        self, client: TestClient, auth_headers: dict, test_interviewer: Interviewer
    ):
        """Successfully list interviewers."""
        response = client.get(
            "/api/v1/interviewers",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1
        assert len(data["items"]) >= 1
        assert data["items"][0]["name"] == "John Doe"
        assert "limit" in data
        assert "offset" in data

    def test_list_interviewers_empty(
        self, client: TestClient, auth_headers: dict
    ):
        """List returns empty when no interviewers exist."""
        response = client.get(
            "/api/v1/interviewers",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["items"] == []

    def test_list_interviewers_pagination(
        self, client: TestClient, auth_headers: dict, db_session: Session, test_user: User
    ):
        """Test pagination parameters."""
        # Create multiple interviewers
        for i in range(5):
            db_session.add(Interviewer(
                user_id=test_user.id,
                name=f"Interviewer {i}",
                company=f"Company {i}",
            ))
        db_session.commit()

        response = client.get(
            "/api/v1/interviewers?limit=2&offset=0",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2
        assert data["total"] == 5
        assert data["limit"] == 2
        assert data["offset"] == 0

    def test_list_interviewers_pagination_offset(
        self, client: TestClient, auth_headers: dict, db_session: Session, test_user: User
    ):
        """Test pagination with offset."""
        # Create multiple interviewers
        for i in range(5):
            db_session.add(Interviewer(
                user_id=test_user.id,
                name=f"Interviewer {i}",
                company=f"Company {i}",
            ))
        db_session.commit()

        response = client.get(
            "/api/v1/interviewers?limit=2&offset=3",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2
        assert data["offset"] == 3

    def test_list_interviewers_user_isolation(
        self,
        client: TestClient,
        auth_headers: dict,
        other_auth_headers: dict,
        test_interviewer: Interviewer,
        other_user: User,
        db_session: Session,
    ):
        """User cannot see other user's interviewers."""
        # Create interviewer for other user
        other_interviewer = Interviewer(
            user_id=other_user.id,
            name="Other's Interviewer",
            company="Other Corp",
        )
        db_session.add(other_interviewer)
        db_session.commit()

        # Get interviewers for other user
        response = client.get("/api/v1/interviewers", headers=other_auth_headers)

        assert response.status_code == 200
        data = response.json()
        # Should only see their own interviewer
        assert data["total"] == 1
        assert data["items"][0]["name"] == "Other's Interviewer"

    def test_list_interviewers_without_auth(self, client: TestClient):
        """Request without auth returns 401."""
        response = client.get("/api/v1/interviewers")

        assert response.status_code == 401


class TestGetInterviewer:
    """Tests for GET /api/v1/interviewers/{id}."""

    def test_get_interviewer_success(
        self, client: TestClient, auth_headers: dict, test_interviewer: Interviewer
    ):
        """Successfully get interviewer by ID."""
        response = client.get(
            f"/api/v1/interviewers/{test_interviewer.id}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(test_interviewer.id)
        assert data["name"] == "John Doe"
        assert data["company"] == "TechCorp"
        assert data["email"] == "john.doe@techcorp.com"
        assert data["profile_status"] == "hidden"

    def test_get_interviewer_not_found(
        self, client: TestClient, auth_headers: dict
    ):
        """Request for non-existent interviewer returns 404."""
        fake_id = uuid4()
        response = client.get(
            f"/api/v1/interviewers/{fake_id}",
            headers=auth_headers,
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "Interviewer not found"

    def test_get_interviewer_other_user(
        self,
        client: TestClient,
        other_auth_headers: dict,
        test_interviewer: Interviewer,
    ):
        """Cannot get another user's interviewer - returns 404."""
        response = client.get(
            f"/api/v1/interviewers/{test_interviewer.id}",
            headers=other_auth_headers,
        )

        # Returns 404 to avoid leaking existence information
        assert response.status_code == 404
        assert response.json()["detail"] == "Interviewer not found"

    def test_get_interviewer_without_auth(
        self, client: TestClient, test_interviewer: Interviewer
    ):
        """Request without auth returns 401."""
        response = client.get(f"/api/v1/interviewers/{test_interviewer.id}")

        assert response.status_code == 401
