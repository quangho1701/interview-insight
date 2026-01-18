"""API dependencies for dependency injection."""

from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session, select

from app.core.config import get_settings, GUEST_USER_ID, GUEST_USER_EMAIL
from app.core.database import get_session
from app.core.security import decode_access_token
from app.models.user import User
from app.models.enums import AuthProvider
from app.services.s3_service import S3Service

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/login/access-token")
oauth2_scheme_optional = OAuth2PasswordBearer(
    tokenUrl="/api/v1/login/access-token",
    auto_error=False,
)


def get_or_create_guest_user(session: Session) -> User:
    """Get or create the dev guest user."""
    guest_id = UUID(GUEST_USER_ID)
    user = session.get(User, guest_id)
    if not user:
        user = User(
            id=guest_id,
            email=GUEST_USER_EMAIL,
            provider=AuthProvider.LOCAL,
            hashed_password=None,
        )
        session.add(user)
        session.commit()
        session.refresh(user)
    return user


def get_current_user(
    token: Annotated[str | None, Depends(oauth2_scheme_optional)],
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
    settings = get_settings()

    # Dev bypass: return guest user when no token provided
    if settings.dev_auth_bypass and token is None:
        return get_or_create_guest_user(session)

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if token is None:
        raise credentials_exception

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
