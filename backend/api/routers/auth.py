from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from api.database.database import get_db
from api.models.platform_permission import PlatformPermission
from api.schemas.admin import PlatformPermissionResponse
from api.models.role import UserRole
from api.models.system_settings import SystemSettings
from typing import Literal

from api.dependencies import get_current_user
from api.models.user import User
from api.schemas.user import UserResponse


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


class ProfileUpdate(BaseModel):
    full_name: str = Field(min_length=1, max_length=150)


class UserPreferences(BaseModel):
    language: Literal["English", "Hindi", "Marathi"] = "English"
    response_style: Literal["Concise", "Detailed"] = "Concise"


def get_user_preferences(db, user):
    record = db.get(SystemSettings, f"user:{user.id}")
    return record.values if record else UserPreferences().model_dump()


@router.get("/preferences")
def preferences_get(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return get_user_preferences(db, current_user)


@router.put("/preferences")
def preferences_put(payload: UserPreferences, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    key = f"user:{current_user.id}"
    record = db.get(SystemSettings, key)
    if record is None:
        record = SystemSettings(id=key, values=payload.model_dump())
        db.add(record)
    else:
        record.values = payload.model_dump()
    db.commit()
    return record.values


@router.patch("/me", response_model=UserResponse)
def update_profile(payload: ProfileUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    name = payload.full_name.strip()
    if not name:
        raise HTTPException(422, "Enter your name.")
    current_user.full_name = name
    db.commit()
    db.refresh(current_user)
    return current_user


@router.get("/permissions", response_model=list[PlatformPermissionResponse])
def permissions(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role in (UserRole.USER, UserRole.LEGAL_PROFESSIONAL):
        return []
    return db.query(PlatformPermission).order_by(PlatformPermission.module_name).all()


# =========================================================
# CURRENT LOGGED-IN USER
# =========================================================

@router.get(
    "/me",
    response_model=UserResponse,
)
async def get_current_logged_in_user(
    current_user: User = Depends(get_current_user),
):
    """
    Return the currently authenticated LegalLens user.

    Authentication is handled by Firebase.
    The Firebase ID token is verified by the backend.
    """

    return current_user


# =========================================================
# CURRENT USER ROLE
# =========================================================

@router.get("/role")
async def get_role(
    current_user: User = Depends(get_current_user),
):
    """
    Return the authenticated user's LegalLens role.
    """

    return {
        "id": str(current_user.id),
        "firebase_uid": current_user.firebase_uid,
        "email": current_user.email,
        "role": current_user.role.value,
        "is_active": current_user.is_active,
    }


# =========================================================
# CHECK ADMIN ACCESS
# =========================================================

@router.get("/is-admin")
async def check_admin(
    current_user: User = Depends(get_current_user),
):
    """
    Check whether the authenticated user has admin access.
    """

    is_admin = current_user.role.value in (
        "admin",
        "super_admin",
    )

    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "role": current_user.role.value,
        "is_admin": is_admin,
    }
