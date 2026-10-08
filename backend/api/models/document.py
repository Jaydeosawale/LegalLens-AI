from datetime import datetime
from uuid import uuid4

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api.database.database import Base


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    user_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    filename: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    original_filename: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    file_path: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    file_url: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    file_type: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    file_size: Mapped[int | None] = mapped_column(
        BigInteger,
        nullable=True,
    )

    # SHA-256 hash for duplicate document detection
    file_hash: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        unique=True,
    )

    processing_status: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default="pending",
    )

    approval_status: Mapped[str] = mapped_column(String(20), default="draft", nullable=False)
    submitted_by: Mapped[str | None] = mapped_column(String(36), nullable=True)
    rag_scope: Mapped[str] = mapped_column(String(20), default="private", nullable=False)
    access_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    reviewed_by: Mapped[str | None] = mapped_column(String(36), nullable=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    review_note: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
    )

    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    chunks = relationship(
        "DocumentChunk",
        back_populates="document",
        cascade="all, delete-orphan",
    )
