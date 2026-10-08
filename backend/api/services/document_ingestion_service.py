import hashlib
import shutil
import tempfile
from pathlib import Path

from fastapi import UploadFile
from sqlalchemy.orm import Session

from api.models.document import Document
from api.models.document_chunk import DocumentChunk
from api.models.document_embedding import DocumentEmbedding
from api.storage.r2_storage import r2_storage

from ingestion.document_loader import DocumentLoader
from rag.chunking.text_splitter import TextSplitter
from rag.embeddings.embeddings import EmbeddingModel


class DocumentIngestionService:
    """
    Handles the complete LegalLens document ingestion pipeline.

    PDF Upload
        ↓
    SHA-256 duplicate detection
        ↓
    Cloudflare R2 storage
        ↓
    PDF extraction / OCR
        ↓
    Chunking
        ↓
    Embeddings
        ↓
    PostgreSQL + pgvector
    """

    @staticmethod
    def calculate_file_hash(file_bytes: bytes) -> str:
        """Generate SHA-256 hash for duplicate detection."""

        return hashlib.sha256(file_bytes).hexdigest()

    @staticmethod
    def create_r2_key(
        file_hash: str,
        filename: str,
    ) -> str:
        """Create an organized R2 object key."""

        safe_filename = Path(filename).name

        return f"documents/{file_hash}/{safe_filename}"

    @classmethod
    def ingest_document(
        cls,
        uploaded_file: UploadFile,
        db: Session,
        user_id: str | None = None,
    ) -> dict:
        """
        Process and store a PDF document.
        """

        # ---------------------------------------------
        # 1. Validate file
        # ---------------------------------------------

        filename = uploaded_file.filename or "document.pdf"

        if not filename.lower().endswith(".pdf"):
            raise ValueError(
                "Only PDF files are supported."
            )

        # ---------------------------------------------
        # 2. Read uploaded file
        # ---------------------------------------------

        file_bytes = uploaded_file.file.read()

        if not file_bytes:
            raise ValueError(
                "Uploaded file is empty."
            )

        if len(file_bytes) > 10 * 1024 * 1024:
            raise ValueError("PDF must be 10 MB or smaller.")

        # ---------------------------------------------
        # 3. Generate SHA-256 hash
        # ---------------------------------------------

        if not user_id:
            raise ValueError("A document owner is required.")
        file_hash = cls.calculate_file_hash(user_id.encode() + b"\0" + file_bytes)

        # ---------------------------------------------
        # 4. Duplicate detection
        # ---------------------------------------------

        existing_document = (
            db.query(Document)
            .filter(Document.file_hash == file_hash)
            .first()
        )

        if existing_document:

            return {
                "success": True,
                "duplicate": True,
                "document_id": existing_document.id,
                "filename": existing_document.original_filename,
                "status": existing_document.processing_status,
                "message": "This document already exists.",
            }

        # ---------------------------------------------
        # 5. Create temporary processing directory
        # ---------------------------------------------

        temp_directory = Path(
            tempfile.mkdtemp(
                prefix="legallens_"
            )
        )

        temp_file_path = (
            temp_directory / Path(filename).name
        )

        document = None
        r2_key = None

        try:

            # -----------------------------------------
            # Save temporary PDF
            # -----------------------------------------

            temp_file_path.write_bytes(file_bytes)

            # -----------------------------------------
            # 6. Create R2 object key
            # -----------------------------------------

            r2_key = cls.create_r2_key(
                file_hash=file_hash,
                filename=filename,
            )

            # -----------------------------------------
            # 7. Upload PDF to Cloudflare R2
            # -----------------------------------------

            with open(temp_file_path, "rb") as file_obj:

                r2_key = r2_storage.upload_file(
                    file_obj=file_obj,
                    object_key=r2_key,
                    content_type="application/pdf",
                )

            # -----------------------------------------
            # 8. Create database document record
            # -----------------------------------------

            document = Document(
                user_id=user_id,
                filename=r2_key,
                original_filename=filename,
                file_path=None,
                file_url=None,
                file_type="application/pdf",
                file_size=len(file_bytes),
                file_hash=file_hash,
                processing_status="processing",
            )

            db.add(document)

            db.commit()
            db.refresh(document)

            # -----------------------------------------
            # 9. Extract PDF text / OCR
            # -----------------------------------------

            documents = DocumentLoader.load_pdf(
                str(temp_file_path)
            )

            if not documents:
                raise ValueError(
                    "No readable text could be extracted "
                    "from the PDF."
                )

            # -----------------------------------------
            # 10. Split documents into chunks
            # -----------------------------------------

            chunks = TextSplitter.split_documents(
                documents
            )

            if not chunks:
                raise ValueError(
                    "No chunks were created."
                )

            # -----------------------------------------
            # 11. Save chunks
            # -----------------------------------------

            chunk_records = []

            for index, chunk in enumerate(chunks):

                chunk_record = DocumentChunk(
                    document_id=document.id,
                    chunk_index=index,
                    content=chunk.page_content,
                    metadata_=chunk.metadata,
                )

                db.add(chunk_record)

                chunk_records.append(chunk_record)

            db.flush()

            # -----------------------------------------
            # 12. Load embedding model
            # -----------------------------------------

            embedding_model = (
                EmbeddingModel.get_model()
            )

            texts = [
                chunk.content
                for chunk in chunk_records
            ]

            # -----------------------------------------
            # 13. Generate embeddings
            # -----------------------------------------

            embeddings = (
                embedding_model.embed_documents(texts)
            )

            if len(embeddings) != len(chunk_records):

                raise ValueError(
                    "Embedding count does not match "
                    "chunk count."
                )

            # -----------------------------------------
            # 14. Save pgvector embeddings
            # -----------------------------------------

            for chunk_record, embedding in zip(
                chunk_records,
                embeddings,
            ):

                embedding_record = DocumentEmbedding(
                    chunk_id=chunk_record.id,
                    embedding=list(embedding),
                )

                db.add(embedding_record)

            # -----------------------------------------
            # 15. Mark document completed
            # -----------------------------------------

            document.processing_status = "completed"

            db.commit()

            return {
                "success": True,
                "duplicate": False,
                "document_id": document.id,
                "filename": document.original_filename,
                "chunks_created": len(chunk_records),
                "status": document.processing_status,
                "message": "Document processed successfully.",
            }

        except Exception:

            db.rollback()

            # -----------------------------------------
            # Mark document as failed
            # -----------------------------------------

            if document is not None:

                try:

                    failed_document = (
                        db.query(Document)
                        .filter(
                            Document.id == document.id
                        )
                        .first()
                    )

                    if failed_document:

                        failed_document.processing_status = "failed"

                        db.commit()

                except Exception:

                    db.rollback()

            raise

        finally:

            # -----------------------------------------
            # Delete temporary processing files
            # -----------------------------------------

            if temp_directory.exists():

                shutil.rmtree(
                    temp_directory,
                    ignore_errors=True,
                )
