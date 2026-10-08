import traceback

from fastapi import APIRouter, Depends, HTTPException
from api.models.chat_history import ChatHistory
from api.models.feedback import Feedback
from api.models.user import User
from sqlalchemy.orm import Session

from api.database.database import get_db
from api.dependencies import get_current_user
from api.schemas.feedback import FeedbackCreate

router = APIRouter(
    prefix="/feedback",
    tags=["Feedback"],
)


# ---------------------------------------------------------
# Save Feedback
# ---------------------------------------------------------

@router.post("/")
def save_feedback(
    feedback: FeedbackCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    try:

        # -----------------------------------------
        # Verify Chat Exists
        # -----------------------------------------

        chat = (
            db.query(ChatHistory)
            .filter(
                ChatHistory.id == feedback.chat_id,
                ChatHistory.user_id == current_user.id,
            )
            .first()
        )

        if chat is None:
            raise HTTPException(
                status_code=404,
                detail="Chat not found.",
            )

        # -----------------------------------------
        # Prevent Duplicate Feedback
        # -----------------------------------------

        existing = (
            db.query(Feedback)
            .filter(
                Feedback.chat_id == feedback.chat_id,
                Feedback.user_id == current_user.id,
            )
            .first()
        )

        if existing:

            existing.helpful = feedback.helpful

            db.commit()
            db.refresh(existing)

            return {
                "success": True,
                "message": "Feedback updated successfully."
            }

        # -----------------------------------------
        # Save New Feedback
        # -----------------------------------------

        obj = Feedback(
            user_id=current_user.id,
            chat_id=feedback.chat_id,
            helpful=feedback.helpful,
        )

        db.add(obj)
        db.commit()
        db.refresh(obj)

        return {
            "success": True,
            "message": "Feedback saved successfully."
        }

    except HTTPException:
        raise

    except Exception as e:

        traceback.print_exc()

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )


# ---------------------------------------------------------
# List Feedback
# ---------------------------------------------------------

@router.get("/")
def list_feedback(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    try:

        feedback = (
            db.query(Feedback)
            .filter(
                Feedback.user_id == current_user.id
            )
            .order_by(
                Feedback.created_at.desc()
            )
            .all()
        )

        return feedback

    except Exception as e:

        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )