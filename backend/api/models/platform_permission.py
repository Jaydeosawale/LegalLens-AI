from datetime import datetime

from sqlalchemy import Boolean, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from api.database.database import Base


class PlatformPermission(Base):
    __tablename__ = "platform_permissions"

    # =========================================================
    # PRIMARY KEY
    # =========================================================

    module_name: Mapped[str] = mapped_column(
        String(100),
        primary_key=True,
    )

    # =========================================================
    # ADMIN ACCESS
    #
    # SUPER_ADMIN always has access.
    # This flag controls ADMIN access only.
    # =========================================================

    enabled_for_admin: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    # =========================================================
    # TIMESTAMP
    # =========================================================

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    def __repr__(self):
        return (
            f"<PlatformPermission("
            f"module_name='{self.module_name}', "
            f"enabled_for_admin={self.enabled_for_admin}"
            f")>"
        )
