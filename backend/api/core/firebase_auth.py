from fastapi import Header, HTTPException, status
from firebase_admin import auth


async def get_current_firebase_user(
    authorization: str | None = Header(default=None),
):
    """
    Verify Firebase ID token from the Authorization header.

    Expected format:

    Authorization: Bearer <firebase_id_token>
    """

    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header is required",
        )

    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format",
        )

    id_token = authorization.split("Bearer ", 1)[1].strip()

    if not id_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Firebase token is required",
        )

    try:
        decoded_token = auth.verify_id_token(id_token)

        return decoded_token

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired Firebase token",
        )
