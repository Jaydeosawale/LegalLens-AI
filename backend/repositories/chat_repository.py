from api.models.chat_history import ChatHistory
from sqlalchemy import func
from sqlalchemy.orm import Session


class ChatRepository:

    @staticmethod
    def create(
        db: Session,
        user_id: str,
        question: str,
        answer: str,
        pdf_name: str | None = None,
        rating: bool | None = None,
    ) -> ChatHistory:

        chat = ChatHistory(
            user_id=user_id,
            question=question,
            answer=answer,
            pdf_name=pdf_name,
            rating=rating,
        )

        db.add(chat)
        db.commit()
        db.refresh(chat)

        return chat

    @staticmethod
    def get_all(
        db: Session,
        user_id: str,
    ) -> list[ChatHistory]:

        return (
            db.query(ChatHistory)
            .filter(ChatHistory.user_id == user_id)
            .order_by(ChatHistory.created_at.desc())
            .all()
        )

    @staticmethod
    def get_count(
        db: Session,
        user_id: str,
    ) -> int:

        return (
            db.query(func.count(ChatHistory.id))
            .filter(ChatHistory.user_id == user_id)
            .scalar()
        )

    @staticmethod
    def delete(
        db: Session,
        chat_id: str,
        user_id: str,
    ) -> bool:

        chat = (
            db.query(ChatHistory)
            .filter(
                ChatHistory.id == chat_id,
                ChatHistory.user_id == user_id,
            )
            .first()
        )

        if not chat:
            return False

        db.delete(chat)
        db.commit()

        return True

    @staticmethod
    def clear(
        db: Session,
        user_id: str,
    ):

        (
            db.query(ChatHistory)
            .filter(ChatHistory.user_id == user_id)
            .delete()
        )

        db.commit()

    @staticmethod
    def update_rating(
        db: Session,
        chat_id: str,
        user_id: str,
        rating: bool,
    ):

        chat = (
            db.query(ChatHistory)
            .filter(
                ChatHistory.id == chat_id,
                ChatHistory.user_id == user_id,
            )
            .first()
        )

        if chat:

            chat.rating = rating

            db.commit()

            db.refresh(chat)

        return chat