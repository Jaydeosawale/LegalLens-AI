import traceback
from typing import Literal
from uuid import uuid4
from pydantic import BaseModel, Field
from sqlalchemy import select

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile,
)
from sqlalchemy.orm import Session

from api.database.database import get_db
from api.core.platform_modules import DOCUMENTS
from api.core.platform_permission_guard import require_platform_module
from api.dependencies import get_current_user
from api.core.document_access import document_query, document_actor
from api.models.document import Document
from api.models.user import User
from api.models.role import UserRole
from api.models.document_chunk import DocumentChunk
from api.models.document_embedding import DocumentEmbedding
from api.models.system_settings import SystemEvent
from api.services.document_review_service import review_document
from api.services.document_ingestion_service import (
    DocumentIngestionService,
)


router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)


class ReviewRequest(BaseModel):
    decision: Literal['approved', 'rejected']
    scope: Literal['private', 'shared'] = 'private'
    note: str = Field(default='', max_length=1000)


class AccessRequest(BaseModel):
    enabled: bool


def review_fields(document, db):
    owner = db.get(User, document.user_id) if document.user_id else None
    return {'approval_status': document.approval_status, 'rag_scope': document.rag_scope,
            'access_enabled': document.access_enabled, 'review_note': document.review_note,
            'reviewed_at': document.reviewed_at, 'submitted_by': document.submitted_by,
            'owner_role': owner.role.value if owner else None}


def managed_document(db, actor, identifier):
    if actor.role not in (UserRole.ADMIN, UserRole.SUPER_ADMIN):
        raise HTTPException(403, 'Administrator access required.')
    document = document_query(db, actor).filter(Document.id == identifier).with_for_update().first()
    if document is None:
        raise HTTPException(404, 'Document not found.')
    return document


@router.post('/{document_id}/submit')
def submit_review(document_id: str, db: Session = Depends(get_db), actor: User = Depends(document_actor)):
    document = managed_document(db, actor, document_id)
    if document.processing_status != 'completed':
        raise HTTPException(409, 'Document processing must finish first.')
    chunk_ids = select(DocumentChunk.id).where(DocumentChunk.document_id == document.id)
    db.query(DocumentEmbedding).filter(DocumentEmbedding.chunk_id.in_(chunk_ids)).delete(synchronize_session=False)
    document.approval_status = 'pending'
    document.rag_scope = 'private'
    document.submitted_by = actor.id
    document.reviewed_by = None
    document.reviewed_at = None
    document.review_note = None
    db.add(SystemEvent(id=str(uuid4()), action=f'Submitted RAG document {document.id} for review', actor=actor.email))
    db.commit()
    return {'success': True, **review_fields(document, db)}


@router.post('/{document_id}/review')
def document_review(document_id: str, payload: ReviewRequest, db: Session = Depends(get_db), actor: User = Depends(document_actor)):
    document = managed_document(db, actor, document_id)
    try:
        review_document(db, document, actor, payload.decision, payload.scope, payload.note)
        return {'success': True, **review_fields(document, db)}
    except Exception:
        db.rollback()
        raise


@router.patch('/{document_id}/access')
def document_access(document_id: str, payload: AccessRequest, db: Session = Depends(get_db), actor: User = Depends(document_actor)):
    document = managed_document(db, actor, document_id)
    document.access_enabled = payload.enabled
    db.add(SystemEvent(id=str(uuid4()), action=f'{"Enabled" if payload.enabled else "Disabled"} document access {document.id}', actor=actor.email))
    db.commit()
    return {'success': True, **review_fields(document, db)}


# ---------------------------------------------------------
# Health Check
# ---------------------------------------------------------

@router.get("/")
def documents_home():
    return {
        "message": "Documents API Working"
    }


# ---------------------------------------------------------
# List Documents
# ---------------------------------------------------------

@router.get("/list")
def list_documents(
    db: Session = Depends(get_db),
    current_user: User = Depends(document_actor),
):
    try:

        documents = (
            document_query(db, current_user)
            .order_by(
                Document.created_at.desc()
            )
            .all()
        )

        result = []

        for document in documents:

            result.append(
                {
                    "id": document.id,
                    "filename": document.original_filename,
                    "file_type": document.file_type,
                    "file_size": document.file_size,
                    "status": document.processing_status,
                    "created_at": document.created_at,
                    **review_fields(document, db),
                }
            )

        return {
            "success": True,
            "documents": result,
            "total_documents": len(result),
        }

    except Exception as e:

        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )


# ---------------------------------------------------------
# Upload Documents
# ---------------------------------------------------------

@router.post("/upload")
def upload_documents(
    files: list[UploadFile] = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(document_actor),
):
    try:

        results = []

        documents_added = 0
        duplicates = 0
        failed = 0

        for uploaded_file in files:

            try:

                result = (
                    DocumentIngestionService.ingest_document(
                        uploaded_file=uploaded_file,
                        db=db,
                        user_id=current_user.id,
                    )
                )

                results.append(result)

                if result.get("duplicate"):
                    duplicates += 1
                else:
                    documents_added += 1

            except Exception as file_error:

                traceback.print_exc()

                failed += 1

                results.append(
                    {
                        "success": False,
                        "filename": uploaded_file.filename,
                        "error": str(file_error),
                    }
                )

        return {
            "success": failed == 0,
            "documents_added": documents_added,
            "duplicates": duplicates,
            "failed": failed,
            "results": results,
        }

    except Exception as e:

        traceback.print_exc()

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )


# ---------------------------------------------------------
# Get Document Details
# ---------------------------------------------------------

@router.get("/{document_id}")
def get_document(
    document_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(document_actor),
):
    try:

        document = (
            document_query(db, current_user)
            .filter(
                Document.id == document_id
            )
            .first()
        )

        if not document:

            raise HTTPException(
                status_code=404,
                detail="Document not found.",
            )

        return {
            "success": True,
            "document": {
                "id": document.id,
                "filename": document.original_filename,
                "file_type": document.file_type,
                "file_size": document.file_size,
                "file_hash": document.file_hash,
                "status": document.processing_status,
                "created_at": document.created_at,
                "updated_at": document.updated_at,
                **review_fields(document, db),
            },
        }

    except HTTPException:
        raise

    except Exception as e:

        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )


# ---------------------------------------------------------
# Delete Document
# ---------------------------------------------------------

@router.delete("/{document_id}")
def delete_document(
    document_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(document_actor),
):
    try:

        document = (
            document_query(db, current_user)
            .filter(
                Document.id == document_id
            )
            .first()
        )

        if not document:

            raise HTTPException(
                status_code=404,
                detail="Document not found.",
            )

        # Delete from database.
        #
        # Related chunks and embeddings are automatically
        # deleted because of CASCADE relationships.

        db.delete(document)

        db.commit()

        return {
            "success": True,
            "message": "Document deleted successfully.",
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
