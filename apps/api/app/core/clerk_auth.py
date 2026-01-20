"""Clerk JWT token verification using JWKS."""

from functools import lru_cache
from typing import Any

import jwt
from jwt import PyJWKClient, PyJWTError

from app.core.config import get_settings


class ClerkAuthError(Exception):
    """Raised when Clerk token verification fails."""

    pass


@lru_cache()
def get_jwk_client() -> PyJWKClient:
    """Get cached JWK client for Clerk JWKS endpoint."""
    settings = get_settings()
    if not settings.clerk_jwks_url:
        raise ClerkAuthError("CLERK_JWKS_URL not configured")
    return PyJWKClient(settings.clerk_jwks_url)


def verify_clerk_token(token: str) -> dict[str, Any]:
    """Verify and decode a Clerk JWT token.

    Args:
        token: The JWT token string from Authorization header.

    Returns:
        Decoded token payload containing 'sub' (Clerk user ID) and claims.

    Raises:
        ClerkAuthError: If token is invalid, expired, or verification fails.
    """
    settings = get_settings()

    if not settings.clerk_issuer:
        raise ClerkAuthError("CLERK_ISSUER not configured")

    try:
        jwk_client = get_jwk_client()
        signing_key = jwk_client.get_signing_key_from_jwt(token)

        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            issuer=settings.clerk_issuer,
            options={"verify_aud": False},  # Clerk doesn't always include aud
        )
        return payload

    except PyJWTError as e:
        raise ClerkAuthError(f"Token verification failed: {str(e)}")
