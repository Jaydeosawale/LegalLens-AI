from fastapi import Depends, HTTPException, status

from api.core.current_user import (
    get_current_firebase_db_user,
)
from api.models.role import UserRole
from api.models.user import User


# =========================================================
# CURRENT AUTHENTICATED USER
# =========================================================

async def get_current_user(
    current_user: User = Depends(
        get_current_firebase_db_user,
    ),
):
    return current_user


# =========================================================
# CURRENT ADMIN
# =========================================================

async def get_current_admin(
    current_user: User = Depends(get_current_user),
):
    if current_user.role not in (
        UserRole.ADMIN,
        UserRole.SUPER_ADMIN,
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )

    return current_user


# =========================================================
# CURRENT SUPER ADMIN
# =========================================================

async def get_current_super_admin(
    current_user: User = Depends(get_current_user),
):
    if current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super Admin access required",
        )

    return current_user
