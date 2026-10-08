from datetime import datetime
from sqlalchemy import JSON, DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from api.database.database import Base


class SystemSettings(Base):
    __tablename__ = "system_settings"
    id: Mapped[str] = mapped_column(String(100), primary_key=True, default="default")
    values: Mapped[dict] = mapped_column(JSON, nullable=False)


class SystemEvent(Base):
    __tablename__ = "system_events"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    action: Mapped[str] = mapped_column(Text, nullable=False)
    actor: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
