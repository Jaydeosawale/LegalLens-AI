from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from api.database.database import get_db
from api.dependencies import get_current_user
from api.models.conversation import Conversation
from api.models.message import Message
from api.models.user import User

router = APIRouter(prefix="/conversations", tags=["Conversations"])


class ConversationTitle(BaseModel):
    title: str = Field(min_length=1, max_length=255)


def owned_conversation(db: Session, conversation_id: UUID, user: User):
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id, Conversation.user_id == user.id
    ).first()
    if conversation is None:
        raise HTTPException(404, "Conversation not found.")
    return conversation


def summary(conversation):
    return {
        "id": str(conversation.id), "title": conversation.title,
        "created_at": conversation.created_at, "updated_at": conversation.updated_at,
    }


@router.get("/")
def list_conversations(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return [summary(c) for c in db.query(Conversation).filter(
        Conversation.user_id == user.id, Conversation.is_archived.is_(False)
    ).order_by(Conversation.updated_at.desc()).all()]


@router.get("/{conversation_id}")
def get_conversation(conversation_id: UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    conversation = owned_conversation(db, conversation_id, user)
    messages = db.query(Message).filter(Message.conversation_id == conversation.id).order_by(Message.created_at).all()
    return {**summary(conversation), "messages": [
        {"id": str(m.id), "role": m.role, "content": m.content,
         "citations": m.citations or [], "created_at": m.created_at} for m in messages
    ]}


@router.patch("/{conversation_id}")
def rename_conversation(conversation_id: UUID, payload: ConversationTitle, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    conversation = owned_conversation(db, conversation_id, user)
    title = payload.title.strip()
    if not title:
        raise HTTPException(422, "Enter a conversation title.")
    conversation.title = title
    conversation.updated_at = datetime.utcnow()
    db.commit()
    return summary(conversation)


@router.delete("/{conversation_id}", status_code=204)
def delete_conversation(conversation_id: UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    conversation = owned_conversation(db, conversation_id, user)
    db.delete(conversation)
    db.commit()
    return Response(status_code=204)
