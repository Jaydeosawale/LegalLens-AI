from fastapi import Depends, HTTPException, status
from api.models.role import UserRole
from api.models.user import User

from api.dependencies import get_current_user


def get_current_admin(
    current_user: User = Depends(get_current_user),
):
    """
    Allows both ADMIN and SUPER_ADMIN users.
    """

    if current_user.role not in (
        UserRole.ADMIN,
        UserRole.SUPER_ADMIN,
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required.",
        )

    return current_user


def get_current_super_admin(
    current_user: User = Depends(get_current_user),
):
    """
    Allows only SUPER_ADMIN users.
    """

    if current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super Admin access required.",
        )

    return current_user