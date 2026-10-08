from sqlalchemy.orm import Session

from api.core.platform_modules import ALL_PLATFORM_MODULES
from api.models.platform_permission import PlatformPermission


def initialize_platform_permissions(db: Session) -> None:
    """
    Ensure every LegalLens platform module has a permission record.

    Existing records are never overwritten.
    """

    for module_name in ALL_PLATFORM_MODULES:
        existing = (
            db.query(PlatformPermission)
            .filter(
                PlatformPermission.module_name == module_name
            )
            .first()
        )

        if existing is None:
            permission = PlatformPermission(
                module_name=module_name,
                enabled_for_admin=True,
            )

            db.add(permission)

    db.commit()
