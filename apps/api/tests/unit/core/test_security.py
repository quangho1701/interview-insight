"""Unit tests for security module."""

import time
from datetime import timedelta

import pytest

from app.core.security import (
    create_access_token,
    decode_access_token,
    get_password_hash,
    verify_password,
)


class TestPasswordHashing:
    """Tests for password hashing functions."""

    def test_get_password_hash_returns_hash(self):
        """Password hash should be different from plain password."""
        password = "mysecretpassword"
        hashed = get_password_hash(password)

        assert hashed != password
        assert len(hashed) > 0

    def test_get_password_hash_produces_bcrypt_format(self):
        """Hash should be in bcrypt format (starts with $2b$)."""
        password = "testpassword123"
        hashed = get_password_hash(password)

        assert hashed.startswith("$2b$")

    def test_verify_password_with_correct_password(self):
        """Verification should succeed with correct password."""
        password = "correctpassword"
        hashed = get_password_hash(password)

        assert verify_password(password, hashed) is True

    def test_verify_password_with_incorrect_password(self):
        """Verification should fail with incorrect password."""
        password = "correctpassword"
        hashed = get_password_hash(password)

        assert verify_password("wrongpassword", hashed) is False

    def test_different_passwords_produce_different_hashes(self):
        """Different passwords should produce different hashes."""
        hash1 = get_password_hash("password1")
        hash2 = get_password_hash("password2")

        assert hash1 != hash2

    def test_same_password_produces_different_hashes(self):
        """Same password hashed twice should produce different hashes (salting)."""
        password = "samepassword"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)

        assert hash1 != hash2
        # But both should verify correctly
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True


class TestJWTTokens:
    """Tests for JWT token functions."""

    def test_create_access_token_returns_string(self):
        """Access token should be a non-empty string."""
        token = create_access_token(subject="user-123")

        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_access_token_contains_three_parts(self):
        """JWT should have header.payload.signature format."""
        token = create_access_token(subject="user-123")
        parts = token.split(".")

        assert len(parts) == 3

    def test_decode_access_token_returns_payload(self):
        """Decoding valid token should return payload with subject."""
        user_id = "user-456"
        token = create_access_token(subject=user_id)

        payload = decode_access_token(token)

        assert payload is not None
        assert payload["sub"] == user_id
        assert "exp" in payload

    def test_decode_access_token_with_invalid_token(self):
        """Decoding invalid token should return None."""
        payload = decode_access_token("invalid.token.here")

        assert payload is None

    def test_decode_access_token_with_tampered_token(self):
        """Decoding tampered token should return None."""
        token = create_access_token(subject="user-123")
        # Tamper with the token
        tampered = token[:-5] + "XXXXX"

        payload = decode_access_token(tampered)

        assert payload is None

    def test_create_access_token_with_custom_expiry(self):
        """Token should respect custom expiration delta."""
        # Create token with very short expiry
        token = create_access_token(
            subject="user-789",
            expires_delta=timedelta(seconds=1),
        )

        # Should be valid immediately
        payload = decode_access_token(token)
        assert payload is not None

        # Wait for expiration
        time.sleep(2)

        # Should be expired now
        expired_payload = decode_access_token(token)
        assert expired_payload is None
