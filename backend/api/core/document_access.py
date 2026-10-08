from api.models.document import Document
from api.models.role import UserRole
from fastapi import Depends
from api.database.database import get_db
from api.dependencies import get_current_user
from api.core.platform_permission_guard import require_platform_module
from api.core.platform_modules import DOCUMENTS
from sqlalchemy import or_, false
from api.models.user import User
from api.models.platform_permission import PlatformPermission


def document_actor(db=Depends(get_db), user=Depends(get_current_user)):
    if user.role in (UserRole.ADMIN, UserRole.SUPER_ADMIN):
        return require_platform_module(DOCUMENTS)(db, user)
    return user


def document_query(db, user):
    query = db.query(Document)
    if user.role not in (UserRole.ADMIN, UserRole.SUPER_ADMIN):
        query = query.filter(Document.user_id == user.id)
    return query


def rag_document_query(db, user_id, document_ids=None):
    user = db.get(User, user_id)
    query = db.query(Document).filter(
        Document.processing_status == 'completed',
        Document.approval_status == 'approved',
        Document.access_enabled.is_(True),
    )
    if user is None or not user.is_active:
        return query.filter(false())
    permission = db.query(PlatformPermission).filter_by(module_name=DOCUMENTS).first()
    can_manage = user.role == UserRole.SUPER_ADMIN or (
        user.role == UserRole.ADMIN and permission is not None and permission.enabled_for_admin
    )
    if not (can_manage and document_ids is not None):
        query = query.filter(or_(Document.user_id == user_id, Document.rag_scope == 'shared'))
    if document_ids is not None:
        query = query.filter(Document.id.in_(document_ids))
    return query
