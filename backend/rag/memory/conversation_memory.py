from langchain_core.messages import (
    AIMessage,
    HumanMessage,
)


class ConversationMemory:
    """
    Singleton conversation memory used by FastAPI.

    Stores the chat history in memory while the application
    is running. This can later be replaced with Redis,
    a database, or per-user session storage.
    """

    _memory = []

    @classmethod
    def initialize(cls):
        """
        Clear all conversation history.
        """
        cls._memory = []

    @classmethod
    def get_messages(cls):
        """
        Return all conversation messages.
        """
        return cls._memory

    @classmethod
    def add_user_message(cls, question: str):
        """
        Add a user message.
        """
        cls._memory.append(
            HumanMessage(
                content=question
            )
        )

    @classmethod
    def add_ai_message(cls, answer: str):
        """
        Add an AI response.
        """
        cls._memory.append(
            AIMessage(
                content=answer
            )
        )

    @classmethod
    def clear(cls):
        """
        Clear the conversation history.
        """
        cls._memory.clear()

    @classmethod
    def size(cls):
        """
        Number of messages currently stored.
        """
        return len(cls._memory)