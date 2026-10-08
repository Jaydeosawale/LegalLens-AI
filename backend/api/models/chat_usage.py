from sqlalchemy import Date, ForeignKey, Integer, String
from sqlalchemy.orm import mapped_column
from api.database.database import Base


class ChatUsage(Base):
    __tablename__ = "chat_usage"
    user_id = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    usage_day = mapped_column(Date, primary_key=True)
    message_count = mapped_column(Integer, nullable=False, default=0)
