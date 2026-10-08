from typing import Any

from pydantic import BaseModel, Field


class ChatResponse(BaseModel):
    chat_id: str
    answer: str
    citations: list[Any] = Field(default_factory=list)
    documents: list[Any] = Field(default_factory=list)


class APIResponse(BaseModel):
    success: bool = True
    message: str = "Success"
    data: Any | None = None


class ErrorResponse(BaseModel):
    success: bool = False
    message: str