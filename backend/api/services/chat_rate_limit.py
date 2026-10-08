from datetime import datetime, timedelta, timezone
from fastapi import HTTPException
from sqlalchemy.dialects.postgresql import insert as postgres_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from api.models.chat_usage import ChatUsage
from api.models.role import UserRole

DAILY_MESSAGE_LIMIT = 10


def reserve_chat_message(db, user, now=None):
    """Atomically reserve an AI request, independent of deletable chat history."""
    if user.role != UserRole.USER:
        return
    now = now or datetime.now(timezone.utc)
    day = now.astimezone(timezone.utc).date()
    reset = datetime.combine(day + timedelta(days=1), datetime.min.time(), timezone.utc)
    insert = postgres_insert if db.bind.dialect.name == "postgresql" else sqlite_insert
    table = ChatUsage.__table__
    statement = insert(table).values(user_id=user.id, usage_day=day, message_count=1)
    statement = statement.on_conflict_do_update(
        index_elements=[table.c.user_id, table.c.usage_day],
        set_={"message_count": table.c.message_count + 1},
        where=table.c.message_count < DAILY_MESSAGE_LIMIT,
    ).returning(table.c.message_count)
    admitted = db.execute(statement).scalar_one_or_none()
    db.commit()
    if admitted is None:
        raise HTTPException(
            429,
            "Daily limit reached: normal accounts can send 10 chat messages per day. "
            "Your limit resets at 00:00 UTC (05:30 IST).",
            headers={"Retry-After": str(max(1, int((reset - now).total_seconds())))},
        )
