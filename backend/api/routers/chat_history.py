from fastapi import APIRouter, Depends, HTTPException
from api.models.chat_history import ChatHistory
from api.models.user import User
from sqlalchemy.orm import Session

from api.database.database import get_db
from api.dependencies import get_current_user
from api.schemas.chat_history import ChatHistoryCreate, ChatHistoryResponse

router = APIRouter(
    prefix="/chat/history",
    tags=["Chat History"],
)


@router.post(
    "",
    response_model=ChatHistoryResponse,
)
def save_chat_history(
    request: ChatHistoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    chat = ChatHistory(
        user_id=current_user.id,
        question=request.question,
        answer=request.answer,
        pdf_name=request.pdf_name,
    )

    db.add(chat)
    db.commit()
    db.refresh(chat)

    return chat


@router.get(
    "",
    response_model=list[ChatHistoryResponse],
)
def get_chat_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    return (
        db.query(ChatHistory)
        .filter(ChatHistory.user_id == current_user.id)
        .order_by(ChatHistory.created_at.desc())
        .all()
    )


@router.delete("/{chat_id}")
def delete_chat_history(
    chat_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    chat = (
        db.query(ChatHistory)
        .filter(
            ChatHistory.id == chat_id,
            ChatHistory.user_id == current_user.id,
        )
        .first()
    )

    if chat is None:
        raise HTTPException(
            status_code=404,
            detail="Chat history not found.",
        )

    db.delete(chat)
    db.commit()

    return {
        "message": "Chat deleted successfully."
    }