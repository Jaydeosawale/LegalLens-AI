from datetime import datetime

from api.models.role import UserRole
from pydantic import BaseModel, ConfigDict

# ---------------------------------------------------------
# Dashboard Statistics
# ---------------------------------------------------------

class DashboardStats(BaseModel):
    total_users: int
    total_chats: int
    total_documents: int
    total_feedback: int
    positive_feedback: int
    negative_feedback: int

    model_config = ConfigDict(
        from_attributes=True
    )


# ---------------------------------------------------------
# User Summary
# ---------------------------------------------------------

class UserSummary(BaseModel):
    id: str
    full_name: str
    email: str
    role: UserRole
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


# ---------------------------------------------------------
# Chat Summary
# ---------------------------------------------------------

class ChatSummary(BaseModel):
    id: str
    user_email: str
    question: str
    answer: str
    pdf_name: str | None = None
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


# ---------------------------------------------------------
# Document Summary
# ---------------------------------------------------------

class DocumentSummary(BaseModel):
    filename: str
    size: float

    model_config = ConfigDict(
        from_attributes=True
    )

# =========================================================
# PLATFORM PERMISSIONS
# =========================================================

class PlatformPermissionResponse(BaseModel):
    module_name: str
    enabled_for_admin: bool
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )


class UpdatePlatformPermissionRequest(BaseModel):
    enabled_for_admin: bool



# =========================================================
# USER ROLE MANAGEMENT
#
# Only SUPER_ADMIN can change platform roles.
# =========================================================

class UpdateUserRoleRequest(BaseModel):
    role: UserRole


class UserRoleUpdateResponse(BaseModel):
    id: str
    email: str
    full_name: str
    role: UserRole
    is_active: bool

    model_config = ConfigDict(
        from_attributes=True,
    )
