from datetime import datetime
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, String
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api.database.database import Base
from api.models.role import UserRole


class User(Base):
    __tablename__ = "users"

    # =========================================================
    # INTERNAL LEGALLENS USER ID
    # =========================================================

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    # =========================================================
    # FIREBASE IDENTITY
    # =========================================================

    firebase_uid: Mapped[str | None] = mapped_column(
        String(128),
        unique=True,
        index=True,
        nullable=True,
    )

    # =========================================================
    # USER PROFILE
    # =========================================================

    full_name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )

    # Firebase manages passwords for Firebase users.
    # Legacy/local users may still have a password hash.
    password_hash: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    # =========================================================
    # ACCOUNT STATUS
    # =========================================================

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    # =========================================================
    # AUTHORIZATION
    # =========================================================

    role: Mapped[UserRole] = mapped_column(
        SQLEnum(
            UserRole,
            values_callable=lambda enum: [
                e.value for e in enum
            ],
            native_enum=False,
            length=32,
            validate_strings=True,
        ),
        default=UserRole.USER,
        nullable=False,
    )

    # =========================================================
    # TIMESTAMPS
    # =========================================================

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    # =========================================================
    # RELATIONSHIPS
    # =========================================================

    chat_history = relationship(
        "ChatHistory",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    feedback = relationship(
        "Feedback",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return (
            f"<User("
            f"id={self.id}, "
            f"firebase_uid={self.firebase_uid}, "
            f"email='{self.email}', "
            f"role='{self.role.value}', "
            f"is_active={self.is_active}"
            f")>"
        )
