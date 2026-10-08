from pydantic import BaseModel, ConfigDict


class AnalyticsResponse(BaseModel):
    total_chats: int
    total_feedback: int
    positive: int
    negative: int
    helpful_percentage: float

    model_config = ConfigDict(
        from_attributes=True
    )