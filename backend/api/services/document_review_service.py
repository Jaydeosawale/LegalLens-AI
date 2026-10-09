from datetime import datetime, timezone
import hashlib
import math
from uuid import uuid4
from fastapi import HTTPException
from sqlalchemy import insert, select
from api.models.document import Document
from api.models.document_chunk import DocumentChunk
from api.models.document_embedding import DocumentEmbedding
from api.models.role import UserRole
from api.models.user import User
from api.models.system_settings import SystemEvent
from rag.embeddings.embeddings import EmbeddingModel


def review_document(db, document, reviewer, decision, scope, note, precomputed_embeddings=None):
    if reviewer.role != UserRole.SUPER_ADMIN:
        raise HTTPException(403, 'Only the super admin can approve or reject RAG documents.')
    if decision == 'approved':
        if document.approval_status != 'pending' or not document.submitted_by:
            raise HTTPException(409, 'An administrator must submit this document for review first.')
        if document.processing_status != 'completed':
            raise HTTPException(409, 'Document processing must finish before approval.')
        owner = db.get(User, document.user_id) if document.user_id else None
        if scope == 'shared' and (owner is None or owner.role not in (UserRole.ADMIN, UserRole.SUPER_ADMIN)):
            raise HTTPException(422, 'Personal user uploads must remain private.')
    elif precomputed_embeddings is not None:
        raise HTTPException(422, 'Embeddings are only accepted for approval.')
    supplied = None
    if precomputed_embeddings is not None:
        supplied = {item.chunk_index: item for item in precomputed_embeddings}
        if len(supplied) != len(precomputed_embeddings):
            raise HTTPException(422, 'Duplicate chunk indexes in supplied embeddings.')
    model = None
    try:
        chunk_ids = select(DocumentChunk.id).where(DocumentChunk.document_id == document.id)
        db.query(DocumentEmbedding).filter(DocumentEmbedding.chunk_id.in_(chunk_ids)).delete(synchronize_session=False)
        if decision == 'approved':
            last_index = -1
            indexed = 0
            if supplied is None:
                model = EmbeddingModel.get_model()
            while True:
                rows = db.execute(
                    select(DocumentChunk.id, DocumentChunk.content, DocumentChunk.chunk_index)
                    .where(DocumentChunk.document_id == document.id, DocumentChunk.chunk_index > last_index)
                    .order_by(DocumentChunk.chunk_index)
                    .limit(8)
                ).all()
                if not rows:
                    break
                if supplied is None:
                    vectors = model.embed_documents([row.content for row in rows])
                else:
                    vectors = []
                    for row in rows:
                        item = supplied.get(row.chunk_index)
                        if item is None or item.content_sha256 != hashlib.sha256(row.content.encode()).hexdigest():
                            raise HTTPException(422, 'Supplied embeddings do not match document chunks.')
                        if len(item.embedding) != 384 or not all(math.isfinite(value) for value in item.embedding):
                            raise HTTPException(422, 'Supplied embedding has invalid dimensions or values.')
                        vectors.append(item.embedding)
                if len(vectors) != len(rows):
                    raise HTTPException(503, 'Document indexing failed. Please retry.')
                db.execute(insert(DocumentEmbedding), [
                    {'id': str(uuid4()), 'chunk_id': row.id, 'embedding': list(vector)}
                    for row, vector in zip(rows, vectors)
                ])
                indexed += len(rows)
                last_index = rows[-1].chunk_index
            if not indexed:
                raise HTTPException(409, 'This document has no extracted content.')
            if supplied is not None and indexed != len(supplied):
                raise HTTPException(422, 'Supplied embeddings do not match document chunk count.')
        document.approval_status = decision
        document.rag_scope = scope if decision == 'approved' else 'private'
        document.reviewed_by = reviewer.id
        document.reviewed_at = datetime.now(timezone.utc)
        document.review_note = note
        db.add(SystemEvent(id=str(uuid4()), action=f'{decision.title()} RAG document {document.id} ({document.rag_scope})', actor=reviewer.email))
        db.commit()
        return document
    finally:
        if model is not None:
            del model
            EmbeddingModel.release_model()
