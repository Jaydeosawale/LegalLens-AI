from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from api.database.database import get_db
from api.dependencies import get_current_user
from api.models.platform_permission import PlatformPermission
from api.models.role import UserRole
from api.models.user import User


def require_platform_module(module_name: str):
    """
    Create a dependency that protects a platform module.

    SUPER_ADMIN:
        Always allowed.

    ADMIN:
        Allowed only when the module is enabled_for_admin.

    NORMAL USER:
        Never allowed.
    """

    def permission_guard(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
    ) -> User:

        # =====================================================
        # SUPER ADMIN
        # =====================================================

        if current_user.role == UserRole.SUPER_ADMIN:
            return current_user

        # =====================================================
        # NORMAL USER
        # =====================================================

        if current_user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required.",
            )

        # =====================================================
        # ADMIN PLATFORM PERMISSION
        # =====================================================

        permission = (
            db.query(PlatformPermission)
            .filter(
                PlatformPermission.module_name == module_name
            )
            .first()
        )

        if permission is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Module '{module_name}' is not available.",
            )

        if not permission.enabled_for_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    f"Access to '{module_name}' "
                    "has been disabled for administrators."
                ),
            )

        return current_user

    return permission_guard
