from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from api.models.chat_history import ChatHistory
from api.models.feedback import Feedback
from api.models.user import User
from api.models.document import Document
from api.models.role import UserRole
from api.models.platform_permission import PlatformPermission
from api.core.platform_modules import (
    ALL_PLATFORM_MODULES,
    DASHBOARD,
    DOCUMENTS,
    USERS,
    RESEARCH_HISTORY,
    ANALYTICS,
)
from api.core.platform_permission_guard import (
    require_platform_module,
)
from sqlalchemy import func
from sqlalchemy.orm import Session
from pydantic import BaseModel
from api.database.database import get_db
from api.dependencies import (
    get_current_admin,
    get_current_super_admin,
)
from api.schemas.admin import (
    ChatSummary,
    DashboardStats,
    DocumentSummary,
    UserSummary,
    PlatformPermissionResponse,
    UpdatePlatformPermissionRequest,
    UpdateUserRoleRequest,
    UserRoleUpdateResponse,
)

router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
)


class UserStatusUpdate(BaseModel):
    is_active: bool


@router.put("/users/{user_id}/status", response_model=UserRoleUpdateResponse)
def update_user_status(user_id: str, payload: UserStatusUpdate, db: Session = Depends(get_db), current_user: User = Depends(require_platform_module(USERS))):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(404, "User not found.")
    if user.id == current_user.id or user.role == UserRole.SUPER_ADMIN:
        raise HTTPException(403, "Super administrator accounts cannot be disabled.")
    if current_user.role == UserRole.ADMIN and user.role == UserRole.ADMIN:
        raise HTTPException(403, "Only a super administrator can manage administrators.")
    user.is_active = payload.is_active
    db.commit()
    db.refresh(user)
    return user


# ---------------------------------------------------------
# Dashboard
# ---------------------------------------------------------

@router.get(
    "/dashboard",
    response_model=DashboardStats,
)
def dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_platform_module(DASHBOARD),
    ),
):

    total_users = db.query(func.count(User.id)).scalar() or 0
    total_chats = db.query(func.count(ChatHistory.id)).scalar() or 0
    total_feedback = db.query(func.count(Feedback.id)).scalar() or 0

    positive = (
        db.query(func.count(Feedback.id))
        .filter(Feedback.helpful.is_(True))
        .scalar()
        or 0
    )

    negative = (
        db.query(func.count(Feedback.id))
        .filter(Feedback.helpful.is_(False))
        .scalar()
        or 0
    )

    total_documents = db.query(func.count(Document.id)).filter(Document.processing_status == "completed").scalar() or 0

    return DashboardStats(
        total_users=total_users,
        total_chats=total_chats,
        total_documents=total_documents,
        total_feedback=total_feedback,
        positive_feedback=positive,
        negative_feedback=negative,
    )


@router.get("/analytics", response_model=DashboardStats)
def platform_analytics(db: Session = Depends(get_db), current_user: User = Depends(require_platform_module(ANALYTICS))):
    return dashboard(db, current_user)


# ---------------------------------------------------------
# Users
# ---------------------------------------------------------

@router.get(
    "/users",
    response_model=list[UserSummary],
)
def get_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_platform_module(USERS),
    ),
):

    users = (
        db.query(User)
        .order_by(User.created_at.desc())
        .all()
    )

    return [
        UserSummary(
            id=str(user.id),
            full_name=user.full_name,
            email=user.email,
            role=user.role,
            is_active=user.is_active,
            created_at=user.created_at,
        )
        for user in users
    ]


@router.delete("/users/{user_id}")
def delete_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_platform_module(USERS),
    ),
):

    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found.",
        )

    if user.id == current_user.id or user.role == UserRole.SUPER_ADMIN:
        raise HTTPException(403, "This account cannot be deleted.")
    if current_user.role != UserRole.SUPER_ADMIN and user.role != UserRole.USER:
        raise HTTPException(403, "Only a super administrator can manage administrators.")
    db.delete(user)
    db.commit()

    return {
        "message": "User deleted successfully."
    }


# ---------------------------------------------------------
# Chats
# ---------------------------------------------------------

@router.get(
    "/chats",
    response_model=list[ChatSummary],
)
def get_all_chats(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_platform_module(RESEARCH_HISTORY),
    ),
):

    chats = (
        db.query(ChatHistory)
        .order_by(ChatHistory.created_at.desc())
        .all()
    )

    results = []

    for chat in chats:

        user = (
            db.query(User)
            .filter(User.id == chat.user_id)
            .first()
        )

        results.append(
            ChatSummary(
                id=str(chat.id),
                user_email=user.email if user else "",
                question=chat.question,
                answer=chat.answer,
                pdf_name=chat.pdf_name,
                created_at=chat.created_at,
            )
        )

    return results


@router.delete("/chats/{chat_id}")
def delete_chat(
    chat_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_platform_module(RESEARCH_HISTORY),
    ),
):

    chat = (
        db.query(ChatHistory)
        .filter(ChatHistory.id == chat_id)
        .first()
    )

    if not chat:
        raise HTTPException(
            status_code=404,
            detail="Chat not found.",
        )

    db.delete(chat)
    db.commit()

    return {
        "message": "Chat deleted successfully."
    }


# ---------------------------------------------------------
# Documents
# ---------------------------------------------------------

@router.get(
    "/documents",
    response_model=list[DocumentSummary],
)
def get_documents(
    current_user: User = Depends(
        require_platform_module(DOCUMENTS),
    ),
):

    upload_folder = Path("data/uploads")

    if not upload_folder.exists():
        return []

    documents = []

    for file in upload_folder.glob("*.pdf"):

        documents.append(
            DocumentSummary(
                filename=file.name,
                size=round(file.stat().st_size / 1024, 2),
            )
        )

    return documents


# =========================================================
# USER ROLE MANAGEMENT
#
# Only SUPER_ADMIN can promote/demote users.
# SUPER_ADMIN role cannot be assigned through this endpoint.
# =========================================================

@router.put(
    "/users/{user_id}/role",
    response_model=UserRoleUpdateResponse,
)
def update_user_role(
    user_id: str,
    payload: UpdateUserRoleRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_platform_module(USERS)),
):
    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found.",
        )

    # Safety:
    # This endpoint manages USER <-> ADMIN only.
    # SUPER_ADMIN cannot be created from the UI/API.
    if current_user.role == UserRole.ADMIN and (
        user.role not in (UserRole.USER, UserRole.LEGAL_PROFESSIONAL)
        or payload.role not in (UserRole.USER, UserRole.LEGAL_PROFESSIONAL)
    ):
        raise HTTPException(403, "Only a super administrator can manage administrator roles.")
    if payload.role == UserRole.SUPER_ADMIN:
        raise HTTPException(
            status_code=403,
            detail=(
                "SUPER_ADMIN role cannot be assigned "
                "through this endpoint."
            ),
        )

    # Protect Super Admin accounts.
    if user.role == UserRole.SUPER_ADMIN:
        raise HTTPException(
            status_code=403,
            detail=(
                "SUPER_ADMIN accounts cannot be modified "
                "through this endpoint."
            ),
        )

    # Only USER and ADMIN transitions are allowed.
    if payload.role not in (
        UserRole.USER,
        UserRole.LEGAL_PROFESSIONAL,
        UserRole.ADMIN,
    ):
        raise HTTPException(
            status_code=400,
            detail="Invalid role change.",
        )

    user.role = payload.role

    db.commit()
    db.refresh(user)

    return UserRoleUpdateResponse(
        id=str(user.id),
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        is_active=user.is_active,
    )


# =========================================================
# PLATFORM PERMISSIONS
#
# SUPER_ADMIN controls which modules ADMIN users can access.
# SUPER_ADMIN always has full access.
# =========================================================

@router.get(
    "/platform-permissions",
    response_model=list[PlatformPermissionResponse],
)
def get_platform_permissions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_super_admin),
):
    permissions = (
        db.query(PlatformPermission)
        .order_by(PlatformPermission.module_name)
        .all()
    )

    return permissions


@router.put(
    "/platform-permissions/{module_name}",
    response_model=PlatformPermissionResponse,
)
def update_platform_permission(
    module_name: str,
    payload: UpdatePlatformPermissionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_super_admin),
):
    # Validate module name.
    if module_name not in ALL_PLATFORM_MODULES:
        raise HTTPException(
            status_code=404,
            detail=f"Unknown platform module: {module_name}",
        )

    permission = (
        db.query(PlatformPermission)
        .filter(
            PlatformPermission.module_name == module_name
        )
        .first()
    )

    # Safety: create it if somehow missing.
    if permission is None:
        permission = PlatformPermission(
            module_name=module_name,
            enabled_for_admin=payload.enabled_for_admin,
        )

        db.add(permission)

    else:
        permission.enabled_for_admin = payload.enabled_for_admin

    db.commit()
    db.refresh(permission)

    return permission
