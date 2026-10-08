import os
from uuid import uuid4
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from api.database.database import get_db
from api.dependencies import get_current_admin, get_current_super_admin
from api.models.document import Document
from api.models.document_chunk import DocumentChunk
from api.models.document_embedding import DocumentEmbedding
from api.models.system_settings import SystemSettings, SystemEvent
from api.models.user import User
from api.services.system_settings_service import get_system_settings
from api.services.chat_rate_limit import get_chat_limit

router = APIRouter(prefix="/admin/system", tags=["System"])


class SettingsUpdate(BaseModel):
    model_name: str = Field(min_length=1, max_length=100, pattern=r"^[a-zA-Z0-9/_.:-]+$")
    temperature: float = Field(ge=0, le=1)
    top_k: int = Field(ge=2, le=20)


class ChatLimitUpdate(BaseModel):
    normal_user_daily_messages: int = Field(strict=True, ge=10, le=1000)


@router.put("/chat-limits")
def update_chat_limits(payload: ChatLimitUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_super_admin)):
    record = db.get(SystemSettings, "chat_limits")
    old_limit = get_chat_limit(db)
    if record is None:
        record = SystemSettings(id="chat_limits", values=payload.model_dump())
        db.add(record)
    else:
        record.values = payload.model_dump()
    db.add(SystemEvent(id=str(uuid4()), action=f"Updated normal-user daily chat limit from {old_limit} to {payload.normal_user_daily_messages}", actor=user.email))
    db.commit()
    return record.values


@router.get("")
def get_system(db: Session = Depends(get_db), user: User = Depends(get_current_admin)):
    db.execute(text("SELECT 1"))
    return {"settings": get_system_settings(db), "chat_limits": {"normal_user_daily_messages": get_chat_limit(db)}, "health": {
        "database": "Connected", "ai_credentials": "Configured" if os.getenv("GROQ_API_KEY") else "Missing",
        "documents": db.query(func.count(Document.id)).scalar() or 0,
        "chunks": db.query(func.count(DocumentChunk.id)).scalar() or 0,
        "vectors": db.query(func.count(DocumentEmbedding.id)).scalar() or 0,
    }, "events": [{"action": e.action, "actor": e.actor, "created_at": e.created_at} for e in db.query(SystemEvent).order_by(SystemEvent.created_at.desc()).limit(50).all()]}


@router.put("/settings")
def update_settings(payload: SettingsUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_admin)):
    record = db.get(SystemSettings, "default")
    if record is None:
        record = SystemSettings(id="default", values=payload.model_dump())
        db.add(record)
    else:
        record.values = payload.model_dump()
    db.add(SystemEvent(id=str(uuid4()), action="Updated AI and retrieval configuration", actor=user.email))
    db.commit()
    return record.values
