"""Authentication endpoints."""

from fastapi import APIRouter

from app.api.deps import CurrentUser
from app.models.user import User
from app.schemas.user import UserRead

router = APIRouter()


@router.get("/me", response_model=UserRead)
def get_current_user_info(current_user: CurrentUser) -> User:
    """Get current authenticated user's information.

    Args:
        current_user: Injected current user from Clerk token.

    Returns:
        User information.
    """
    return current_user
