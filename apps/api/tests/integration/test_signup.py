"""Integration tests for user registration endpoint."""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.core.security import get_password_hash, verify_password
from app.models.enums import AuthProvider
from app.models.user import User


class TestUserRegistration:
    """Tests for POST /api/v1/users/."""

    def test_register_user_success(self, client: TestClient, db_session: Session):
        """Successful user registration returns 201 and user data."""
        response = client.post(
            "/api/v1/users/",
            json={
                "email": "newuser@example.com",
                "password": "securepassword123",
                "full_name": "New User",
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "newuser@example.com"
        assert data["provider"] == "local"
        assert data["credits"] == 0
        assert "id" in data
        assert "created_at" in data
        # Password should NOT be in response
        assert "password" not in data
        assert "hashed_password" not in data

    def test_register_user_without_full_name(self, client: TestClient):
        """Registration without full_name succeeds (field is optional)."""
        response = client.post(
            "/api/v1/users/",
            json={
                "email": "nofullname@example.com",
                "password": "securepassword123",
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "nofullname@example.com"

    def test_register_duplicate_email_returns_409(
        self, client: TestClient, db_session: Session
    ):
        """Registering with existing email returns 409 Conflict."""
        # Create existing user
        existing_user = User(
            email="existing@example.com",
            provider=AuthProvider.LOCAL,
            hashed_password=get_password_hash("existingpassword"),
        )
        db_session.add(existing_user)
        db_session.commit()

        # Try to register with same email
        response = client.post(
            "/api/v1/users/",
            json={
                "email": "existing@example.com",
                "password": "newpassword123",
            },
        )

        assert response.status_code == 409
        assert response.json()["detail"] == "Email already registered"

    def test_register_invalid_email_returns_422(self, client: TestClient):
        """Registration with invalid email format returns 422."""
        response = client.post(
            "/api/v1/users/",
            json={
                "email": "not-a-valid-email",
                "password": "securepassword123",
            },
        )

        assert response.status_code == 422

    def test_register_missing_email_returns_422(self, client: TestClient):
        """Registration without email returns 422."""
        response = client.post(
            "/api/v1/users/",
            json={
                "password": "securepassword123",
            },
        )

        assert response.status_code == 422

    def test_register_missing_password_returns_422(self, client: TestClient):
        """Registration without password returns 422."""
        response = client.post(
            "/api/v1/users/",
            json={
                "email": "nopw@example.com",
            },
        )

        assert response.status_code == 422

    def test_register_short_password_returns_422(self, client: TestClient):
        """Registration with password shorter than 8 characters returns 422."""
        response = client.post(
            "/api/v1/users/",
            json={
                "email": "shortpw@example.com",
                "password": "short",  # Less than 8 chars
            },
        )

        assert response.status_code == 422

    def test_password_is_hashed_not_plaintext(
        self, client: TestClient, db_session: Session
    ):
        """Verify password is stored as hash, not plaintext."""
        password = "mysecretpassword"
        response = client.post(
            "/api/v1/users/",
            json={
                "email": "hashtest@example.com",
                "password": password,
            },
        )

        assert response.status_code == 201

        # Fetch user from database
        user = db_session.exec(
            select(User).where(User.email == "hashtest@example.com")
        ).first()

        assert user is not None
        # Password should NOT be stored as plaintext
        assert user.hashed_password != password
        # Password should be verifiable with bcrypt
        assert verify_password(password, user.hashed_password)

    def test_registered_user_has_local_provider(
        self, client: TestClient, db_session: Session
    ):
        """Registered user has LOCAL auth provider set."""
        response = client.post(
            "/api/v1/users/",
            json={
                "email": "providertest@example.com",
                "password": "securepassword123",
            },
        )

        assert response.status_code == 201

        user = db_session.exec(
            select(User).where(User.email == "providertest@example.com")
        ).first()

        assert user is not None
        assert user.provider == AuthProvider.LOCAL


class TestRegisteredUserCanLogin:
    """Tests for signup -> login flow."""

    def test_registered_user_can_login(self, client: TestClient):
        """User can login immediately after registration."""
        # Step 1: Register
        register_response = client.post(
            "/api/v1/users/",
            json={
                "email": "logintest@example.com",
                "password": "mypassword123",
            },
        )
        assert register_response.status_code == 201

        # Step 2: Login
        login_response = client.post(
            "/api/v1/login/access-token",
            data={
                "username": "logintest@example.com",
                "password": "mypassword123",
            },
        )
        assert login_response.status_code == 200
        data = login_response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_registered_user_can_access_protected_route(self, client: TestClient):
        """Full signup -> login -> access protected route flow."""
        # Step 1: Register
        client.post(
            "/api/v1/users/",
            json={
                "email": "fullflow@example.com",
                "password": "securepassword123",
                "full_name": "Full Flow User",
            },
        )

        # Step 2: Login
        login_response = client.post(
            "/api/v1/login/access-token",
            data={
                "username": "fullflow@example.com",
                "password": "securepassword123",
            },
        )
        token = login_response.json()["access_token"]

        # Step 3: Access protected route
        me_response = client.get(
            "/api/v1/me",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert me_response.status_code == 200
        data = me_response.json()
        assert data["email"] == "fullflow@example.com"
        assert data["provider"] == "local"


class TestSignupEdgeCases:
    """Edge case tests for registration."""

    def test_register_with_empty_string_email(self, client: TestClient):
        """Empty string email returns 422."""
        response = client.post(
            "/api/v1/users/",
            json={
                "email": "",
                "password": "securepassword123",
            },
        )

        assert response.status_code == 422

    def test_register_with_whitespace_password(self, client: TestClient):
        """Password with only whitespace is still valid if >= 8 chars."""
        response = client.post(
            "/api/v1/users/",
            json={
                "email": "whitespace@example.com",
                "password": "        ",  # 8 spaces
            },
        )

        # This should succeed - it's 8 characters
        assert response.status_code == 201

    def test_register_unicode_full_name(self, client: TestClient):
        """Registration with unicode characters in full_name succeeds."""
        response = client.post(
            "/api/v1/users/",
            json={
                "email": "unicode@example.com",
                "password": "securepassword123",
                "full_name": "Jose Garcia",
            },
        )

        assert response.status_code == 201

    def test_register_with_long_full_name_returns_422(self, client: TestClient):
        """Registration with full_name exceeding 255 characters returns 422."""
        response = client.post(
            "/api/v1/users/",
            json={
                "email": "longname@example.com",
                "password": "securepassword123",
                "full_name": "A" * 256,  # Exceeds 255 character limit
            },
        )

        assert response.status_code == 422
