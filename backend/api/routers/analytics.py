import traceback

from fastapi import APIRouter, Depends, HTTPException
from api.models.chat_history import ChatHistory
from api.models.feedback import Feedback
from api.models.user import User
from sqlalchemy.orm import Session

from api.database.database import get_db
from api.dependencies import get_current_user
from api.schemas.analytics import AnalyticsResponse

router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"],
)


# ---------------------------------------------------------
# Analytics
# ---------------------------------------------------------

@router.get(
    "/",
    response_model=AnalyticsResponse,
)
def get_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    try:

        # -------------------------------------------------
        # Optional Admin Check
        # -------------------------------------------------

        # Uncomment if analytics should only be visible
        # to administrators.

        # if not current_user.is_admin:
        #     raise HTTPException(
        #         status_code=403,
        #         detail="Administrator access required."
        #     )

        # -------------------------------------------------
        # Total Chats
        # -------------------------------------------------

        total_chats = (
            db.query(ChatHistory)
            .filter(
                ChatHistory.user_id == current_user.id
            )
            .count()
        )

        # -------------------------------------------------
        # Total Feedback
        # -------------------------------------------------

        total_feedback = (
            db.query(Feedback)
            .filter(
                Feedback.user_id == current_user.id
            )
            .count()
        )

        # -------------------------------------------------
        # Positive Feedback
        # -------------------------------------------------

        positive = (
            db.query(Feedback)
            .filter(
                Feedback.user_id == current_user.id,
                Feedback.helpful.is_(True),
            )
            .count()
        )

        # -------------------------------------------------
        # Negative Feedback
        # -------------------------------------------------

        negative = (
            db.query(Feedback)
            .filter(
                Feedback.user_id == current_user.id,
                Feedback.helpful.is_(False),
            )
            .count()
        )

        # -------------------------------------------------
        # Helpful Percentage
        # -------------------------------------------------

        if total_feedback == 0:
            helpful_percentage = 0.0
        else:
            helpful_percentage = round(
                (positive / total_feedback) * 100,
                2,
            )

        # -------------------------------------------------
        # Response
        # -------------------------------------------------

        return AnalyticsResponse(
            total_chats=total_chats,
            total_feedback=total_feedback,
            positive=positive,
            negative=negative,
            helpful_percentage=helpful_percentage,
        )

    except HTTPException:
        raise

    except Exception as e:

        traceback.print_exc()

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )