"""
Database initialization.
"""

from api.database.database import Base, engine

# Import all models so SQLAlchemy registers them
from api.models.user import User
from api.models.chat_history import ChatHistory
from api.models.feedback import Feedback
from api.models.conversation import Conversation
from api.models.message import Message
from api.models.admin_permission import AdminPermission
from api.models.platform_permission import PlatformPermission


def init_db():
    """Create all database tables."""

    Base.metadata.create_all(bind=engine)

    print("Database tables initialized successfully.")


if __name__ == "__main__":
    init_db()