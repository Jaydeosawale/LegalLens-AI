from pydantic import BaseModel, ConfigDict


class FeedbackCreate(BaseModel):
    chat_id: str
    helpful: bool


class FeedbackResponse(BaseModel):
    id: str
    user_id: str
    chat_id: str
    helpful: bool

    model_config = ConfigDict(
        from_attributes=True
    )