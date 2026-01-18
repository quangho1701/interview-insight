"""Authentication endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select

from app.api.deps import CurrentUser, get_or_create_guest_user
from app.core.config import get_settings
from app.core.database import get_session
from app.core.security import create_access_token, verify_password
from app.models.user import User
from app.schemas.token import Token
from app.schemas.user import UserRead

router = APIRouter()


@router.post("/login/access-token", response_model=Token)
def login_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Annotated[Session, Depends(get_session)],
) -> Token:
    """OAuth2 password flow login endpoint.

    Authenticates user with email/password and returns JWT access token.

    Args:
        form_data: OAuth2 form with username (email) and password.
        session: Database session.

    Returns:
        Token with access_token and token_type.

    Raises:
        HTTPException: 401 if credentials are invalid.
    """
    # Find user by email (username field contains email)
    user = session.exec(select(User).where(User.email == form_data.username)).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verify password (only for local auth users)
    if not user.hashed_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token with user ID as subject
    access_token = create_access_token(subject=str(user.id))

    return Token(access_token=access_token)


@router.get("/me", response_model=UserRead)
def get_current_user_info(current_user: CurrentUser) -> User:
    """Get current authenticated user's information.

    Args:
        current_user: Injected current user from JWT.

    Returns:
        User information.
    """
    return current_user


@router.get("/dev-token", response_model=Token)
def get_dev_token(session: Annotated[Session, Depends(get_session)]) -> Token:
    """Get a dev token for the guest user (only available in dev mode).

    Args:
        session: Database session.

    Returns:
        Token with access_token for guest user.

    Raises:
        HTTPException: 404 if dev mode is not enabled.
    """
    settings = get_settings()
    if not settings.dev_auth_bypass:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not found",
        )

    guest_user = get_or_create_guest_user(session)
    access_token = create_access_token(subject=str(guest_user.id))
    return Token(access_token=access_token)
