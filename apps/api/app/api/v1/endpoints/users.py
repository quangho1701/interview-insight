"""User registration endpoints."""

from fastapi import APIRouter, HTTPException, status
from sqlmodel import select

from app.api.deps import SessionDep
from app.core.security import get_password_hash
from app.models.enums import AuthProvider
from app.models.user import User
from app.schemas.user import UserCreate, UserRead

router = APIRouter()


@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(
    data: UserCreate,
    session: SessionDep,
) -> UserRead:
    """Register a new user account.

    Creates a new user with LOCAL authentication provider.
    The password is hashed before storage.

    Args:
        data: User registration data including email and password.
        session: Database session.

    Returns:
        Created user information (without password).

    Raises:
        HTTPException: 409 if email is already registered.
    """
    # Check if email already exists
    existing_user = session.exec(
        select(User).where(User.email == data.email)
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    # Create new user with hashed password
    user = User(
        email=data.email,
        hashed_password=get_password_hash(data.password),
        provider=AuthProvider.LOCAL,
        credits=0,
    )

    session.add(user)
    session.commit()
    session.refresh(user)

    return UserRead.model_validate(user)
