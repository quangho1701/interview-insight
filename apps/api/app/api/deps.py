"""API dependencies for dependency injection."""

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session, select

from app.core.config import get_settings
from app.core.database import get_session
from app.core.security import decode_access_token
from app.models.user import User
from app.services.s3_service import S3Service

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/login/access-token")


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: Annotated[Session, Depends(get_session)],
) -> User:
    """Extract and validate current user from JWT token.

    Args:
        token: Bearer token from Authorization header.
        session: Database session.

    Returns:
        The authenticated User.

    Raises:
        HTTPException: If token is invalid or user not found.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    user_id: str | None = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    user = session.exec(select(User).where(User.id == user_id)).first()
    if user is None:
        raise credentials_exception

    return user


# Type aliases for dependency injection
CurrentUser = Annotated[User, Depends(get_current_user)]
SessionDep = Annotated[Session, Depends(get_session)]


def get_s3_service() -> S3Service:
    """Get S3 service instance."""
    return S3Service(get_settings())


S3ServiceDep = Annotated[S3Service, Depends(get_s3_service)]
