from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

# ============================================================
# Chat Request
# ============================================================

class ChatRequest(BaseModel):
    """
    Request schema for asking a question to the RAG chatbot.
    """

    question: str = Field(
        ...,
        min_length=1,
        description="User question",
        examples=["What is Section 302 of IPC?"],
    )

    conversation_id: UUID | None = Field(
        default=None,
        description="Existing conversation ID. Leave null to create a new conversation.",
    )


# ============================================================
# Chat Response
# ============================================================

class ChatResponse(BaseModel):
    """
    Response schema returned by the RAG chatbot.
    """

    chat_id: str | None = Field(
        default=None,
        description="Saved chat history ID",
    )

    conversation_id: UUID | None = Field(
        default=None,
        description="Conversation ID",
    )

    answer: str = Field(
        ...,
        description="Generated answer",
    )

    citations: list[Any] | None = Field(
        default=None,
        description="Source document names and pages",
    )

    documents: list[Any] | None = Field(
        default=None,
        description="Retrieved document chunks (Admin only)",
    )

    images: list[Any] | None = Field(
        default=None,
        description="Images retrieved using text search.",
    )

    similar_images: list[Any] | None = Field(
        default=None,
        description="Images similar to the uploaded image.",
    )

    image_analysis: str | None = Field(
        default=None,
        description="Analysis or metadata extracted for the uploaded image.",
    )
