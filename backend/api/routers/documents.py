import traceback

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
from api.services.document_ingestion_service import (
    DocumentIngestionService,
)


router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)


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
