from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from api.core.firebase_auth import get_current_firebase_user
from api.database.database import get_db
from api.models.user import User
from api.services.firebase_user_service import FirebaseUserService


async def get_current_firebase_db_user(
    firebase_user: dict = Depends(
        get_current_firebase_user,
    ),
    db: Session = Depends(get_db),
) -> User:
    """
    Verify Firebase identity and return the corresponding
    LegalLens database user.
    """

    try:
        user = FirebaseUserService.get_or_create_user(
            db=db,
            firebase_user=firebase_user,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(error),
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account has been blocked.",
        )

    return user
