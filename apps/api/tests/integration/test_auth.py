"""Integration tests for authentication endpoints."""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.security import create_access_token, get_password_hash
from app.models.enums import AuthProvider
from app.models.user import User


@pytest.fixture
def test_user(db_session: Session) -> User:
    """Create a test user with password for auth tests."""
    user = User(
        email="test@example.com",
        provider=AuthProvider.LOCAL,
        hashed_password=get_password_hash("testpassword123"),
        credits=10,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def oauth_user(db_session: Session) -> User:
    """Create a test user without password (OAuth only)."""
    user = User(
        email="oauth@example.com",
        provider=AuthProvider.GITHUB,
        oauth_id="github-12345",
        credits=5,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


class TestLoginEndpoint:
    """Tests for POST /api/v1/login/access-token."""

    def test_login_with_valid_credentials(self, client: TestClient, test_user: User):
        """Login with correct email and password returns token."""
        response = client.post(
            "/api/v1/login/access-token",
            data={"username": "test@example.com", "password": "testpassword123"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert len(data["access_token"]) > 0

    def test_login_with_invalid_email(self, client: TestClient, test_user: User):
        """Login with non-existent email returns 401."""
        response = client.post(
            "/api/v1/login/access-token",
            data={"username": "nonexistent@example.com", "password": "testpassword123"},
        )

        assert response.status_code == 401
        assert response.json()["detail"] == "Incorrect email or password"

    def test_login_with_invalid_password(self, client: TestClient, test_user: User):
        """Login with wrong password returns 401."""
        response = client.post(
            "/api/v1/login/access-token",
            data={"username": "test@example.com", "password": "wrongpassword"},
        )

        assert response.status_code == 401
        assert response.json()["detail"] == "Incorrect email or password"

    def test_login_oauth_user_without_password(self, client: TestClient, oauth_user: User):
        """OAuth user without password cannot login via password flow."""
        response = client.post(
            "/api/v1/login/access-token",
            data={"username": "oauth@example.com", "password": "anypassword"},
        )

        assert response.status_code == 401
        assert response.json()["detail"] == "Incorrect email or password"


class TestProtectedEndpoints:
    """Tests for protected endpoints requiring authentication."""

    def test_get_me_with_valid_token(self, client: TestClient, test_user: User):
        """GET /me with valid token returns user info."""
        token = create_access_token(subject=str(test_user.id))

        response = client.get(
            "/api/v1/me",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "test@example.com"
        assert data["provider"] == "local"
        assert data["credits"] == 10

    def test_get_me_without_token(self, client: TestClient):
        """GET /me without Authorization header returns 401."""
        response = client.get("/api/v1/me")

        assert response.status_code == 401
        assert response.json()["detail"] == "Not authenticated"

    def test_get_me_with_invalid_token(self, client: TestClient):
        """GET /me with invalid token returns 401."""
        response = client.get(
            "/api/v1/me",
            headers={"Authorization": "Bearer invalid.token.here"},
        )

        assert response.status_code == 401
        assert response.json()["detail"] == "Could not validate credentials"

    def test_get_me_with_malformed_header(self, client: TestClient):
        """GET /me with malformed Authorization header returns 401."""
        response = client.get(
            "/api/v1/me",
            headers={"Authorization": "NotBearer sometoken"},
        )

        assert response.status_code == 401


class TestFullAuthFlow:
    """End-to-end authentication flow tests."""

    def test_login_then_access_protected_route(self, client: TestClient, test_user: User):
        """User can login and use token to access protected routes."""
        # Step 1: Login
        login_response = client.post(
            "/api/v1/login/access-token",
            data={"username": "test@example.com", "password": "testpassword123"},
        )
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]

        # Step 2: Access protected route
        me_response = client.get(
            "/api/v1/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert me_response.status_code == 200
        assert me_response.json()["email"] == "test@example.com"
