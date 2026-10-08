from api.models.document import Document
from api.models.role import UserRole
from fastapi import Depends
from api.database.database import get_db
from api.dependencies import get_current_user
from api.core.platform_permission_guard import require_platform_module
from api.core.platform_modules import DOCUMENTS


def document_actor(db=Depends(get_db), user=Depends(get_current_user)):
    if user.role in (UserRole.ADMIN, UserRole.SUPER_ADMIN):
        return require_platform_module(DOCUMENTS)(db, user)
    return user


def document_query(db, user):
    query = db.query(Document)
    if user.role not in (UserRole.ADMIN, UserRole.SUPER_ADMIN):
        query = query.filter(Document.user_id == user.id)
    return query
