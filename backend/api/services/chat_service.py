from sqlalchemy.orm import Session

from repositories.chat_repository import ChatRepository


class ChatService:

    @staticmethod
    def save_chat(
        db: Session,
        user_id: str,
        question: str,
        answer: str,
        pdf_name: str | None = None,
    ):
        return ChatRepository.create(
            db=db,
            user_id=user_id,
            question=question,
            answer=answer,
            pdf_name=pdf_name,
        )

    @staticmethod
    def get_history(
        db: Session,
        user_id: str,
    ):
        return ChatRepository.get_all(
            db=db,
            user_id=user_id,
        )

    @staticmethod
    def get_chat_count(
        db: Session,
        user_id: str,
    ):
        return ChatRepository.get_count(
            db=db,
            user_id=user_id,
        )

    @staticmethod
    def delete_chat(
        db: Session,
        chat_id: str,
        user_id: str,
    ):
        return ChatRepository.delete(
            db=db,
            chat_id=chat_id,
            user_id=user_id,
        )

    @staticmethod
    def clear_history(
        db: Session,
        user_id: str,
    ):
        ChatRepository.clear(
            db=db,
            user_id=user_id,
        )

    @staticmethod
    def save_feedback(
        db: Session,
        chat_id: str,
        user_id: str,
        rating: bool,
    ):
        return ChatRepository.update_rating(
            db=db,
            chat_id=chat_id,
            user_id=user_id,
            rating=rating,
        )