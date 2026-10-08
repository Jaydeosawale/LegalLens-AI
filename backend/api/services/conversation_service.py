from datetime import datetime
from uuid import UUID

from langchain_core.messages import AIMessage, HumanMessage
from sqlalchemy.orm import Session

from api.models.conversation import Conversation
from api.models.message import Message


class ConversationService:

    """
    Service for managing conversations and messages.
    """

    # -----------------------------------------------------
    # Conversation
    # -----------------------------------------------------

    @staticmethod
    def create_conversation(
        db: Session,
        user_id: UUID,
        title: str = "New Chat",
    ) -> Conversation:

        conversation = Conversation(

            user_id=user_id,

            title=title,

            created_at=datetime.utcnow(),

            updated_at=datetime.utcnow(),

        )

        db.add(conversation)

        db.commit()

        db.refresh(conversation)

        return conversation

    @staticmethod
    def get_conversation(
        db: Session,
        conversation_id: UUID,
        user_id: UUID,
    ) -> Conversation | None:

        return (

            db.query(Conversation)

            .filter(

                Conversation.id == conversation_id,
                Conversation.user_id == user_id,

            )

            .first()

        )

    @staticmethod
    def list_conversations(
        db: Session,
        user_id: UUID,
    ) -> list[Conversation]:

        return (

            db.query(Conversation)

            .filter(

                Conversation.user_id == user_id,

                Conversation.is_archived == False,

            )

            .order_by(

                Conversation.updated_at.desc()

            )

            .all()

        )
            # -----------------------------------------------------
    # Rename Conversation
    # -----------------------------------------------------

    @staticmethod
    def rename_conversation(
        db: Session,
        conversation_id: UUID,
        title: str,
    ) -> bool:

        conversation = (

            db.query(Conversation)

            .filter(

                Conversation.id == conversation_id

            )

            .first()

        )

        if conversation is None:

            return False

        conversation.title = title

        conversation.updated_at = datetime.utcnow()

        db.commit()

        return True

    # -----------------------------------------------------
    # Archive Conversation
    # -----------------------------------------------------

    @staticmethod
    def archive_conversation(
        db: Session,
        conversation_id: UUID,
    ) -> bool:

        conversation = (

            db.query(Conversation)

            .filter(

                Conversation.id == conversation_id

            )

            .first()

        )

        if conversation is None:

            return False

        conversation.is_archived = True

        conversation.updated_at = datetime.utcnow()

        db.commit()

        return True

    # -----------------------------------------------------
    # Delete Conversation
    # -----------------------------------------------------

    @staticmethod
    def delete_conversation(
        db: Session,
        conversation_id: UUID,
    ) -> bool:

        conversation = (

            db.query(Conversation)

            .filter(

                Conversation.id == conversation_id

            )

            .first()

        )

        if conversation is None:

            return False

        db.delete(conversation)

        db.commit()

        return True
            # -----------------------------------------------------
    # Add Message
    # -----------------------------------------------------

    @staticmethod
    def add_message(
        db: Session,
        conversation_id: UUID,
        role: str,
        content: str,
        citations=None,
        documents=None,
        images=None,
    ) -> Message:

        message = Message(

            conversation_id=conversation_id,

            role=role,

            content=content,

            citations=citations,

            documents=documents,

            images=images,

            created_at=datetime.utcnow(),

        )

        db.add(message)

        conversation = (

            db.query(Conversation)

            .filter(

                Conversation.id == conversation_id

            )

            .first()

        )

        if conversation:

            conversation.updated_at = datetime.utcnow()

        db.commit()

        db.refresh(message)

        return message

    # -----------------------------------------------------
    # Get Messages
    # -----------------------------------------------------

    @staticmethod
    def get_messages(
        db: Session,
        conversation_id: UUID,
    ) -> list[Message]:

        return (

            db.query(Message)

            .filter(

                Message.conversation_id == conversation_id

            )

            .order_by(

                Message.created_at.asc()

            )

            .all()

        )

    # -----------------------------------------------------
    # LangChain Messages
    # -----------------------------------------------------

    @staticmethod
    def get_langchain_messages(
        db: Session,
        conversation_id: UUID,
    ):
        """
        Convert database messages into LangChain
        HumanMessage / AIMessage objects.
        """

        messages = ConversationService.get_messages(

            db=db,

            conversation_id=conversation_id,

        )

        history = []

        for msg in messages:

            if msg.role == "user":

                history.append(

                    HumanMessage(

                        content=msg.content

                    )

                )

            else:

                history.append(

                    AIMessage(

                        content=msg.content

                    )

                )

        return history
            # -----------------------------------------------------
    # Update Summary
    # -----------------------------------------------------

    @staticmethod
    def update_summary(
        db: Session,
        conversation_id: UUID,
        summary: str,
    ) -> bool:

        conversation = (

            db.query(Conversation)

            .filter(

                Conversation.id == conversation_id

            )

            .first()

        )

        if conversation is None:

            return False

        conversation.summary = summary

        conversation.updated_at = datetime.utcnow()

        db.commit()

        return True

    # -----------------------------------------------------
    # Auto Title
    # -----------------------------------------------------

    @staticmethod
    def generate_title(
        question: str,
    ) -> str:
        """
        Temporary title generator.
        Later this can be replaced with an LLM.
        """

        question = question.strip()

        if len(question) <= 60:

            return question

        return question[:60] + "..."
