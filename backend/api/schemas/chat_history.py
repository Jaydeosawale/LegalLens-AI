from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ChatHistoryCreate(BaseModel):
    question: str
    answer: str
    pdf_name: str | None = None


class ChatHistoryUpdate(BaseModel):
    rating: bool | None = None


class ChatHistoryResponse(BaseModel):
    id: str
    user_id: str
    question: str
    answer: str
    pdf_name: str | None = None
    rating: bool | None = None
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )