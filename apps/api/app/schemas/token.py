"""Token schemas for authentication."""

from pydantic import BaseModel


class Token(BaseModel):
    """Response schema for access token."""

    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """JWT token payload schema."""

    sub: str  # Subject (user ID)
    exp: int  # Expiration timestamp
