"""Database-ranked keyword retrieval, retaining the legacy retriever interface."""
import re

from langchain_core.documents import Document as LCDocument
from sqlalchemy import func, select, literal_column

from api.core.document_access import rag_document_query
from api.database.database import SessionLocal
from api.models.document import Document
from api.models.document_chunk import DocumentChunk


class PostgresBM25Retriever:
    @staticmethod
    def tokenize(text):
        return re.findall(r"\w+", text.lower())

    @classmethod
    def search_statement(cls, db, question, k, user_id, document_ids):
        allowed = rag_document_query(db, user_id, document_ids).with_entities(Document.id)
        config = literal_column("'english'::regconfig")
        # OR matching preserves partial matches without loading the corpus.
        terms = list(dict.fromkeys(cls.tokenize(question)))[:64]
        query = func.websearch_to_tsquery(config, " OR ".join('"' + term + '"' for term in terms))
        vector = func.to_tsvector(config, DocumentChunk.content)
        rank = func.ts_rank_cd(vector, query, 32).label("score")
        return (
            select(DocumentChunk.id, DocumentChunk.document_id, DocumentChunk.chunk_index,
                   DocumentChunk.content, DocumentChunk.metadata_.label("chunk_metadata"),
                   Document.original_filename, rank)
            .join(Document, DocumentChunk.document_id == Document.id)
            .where(Document.id.in_(allowed.scalar_subquery()), vector.op("@@")(query))
            .order_by(rank.desc(), DocumentChunk.id)
            .limit(max(1, min(k, 50)))
        )

    @classmethod
    def retrieve(cls, question, k=10, user_id=None, document_ids=None):
        if not user_id or k <= 0 or not cls.tokenize(question):
            return []
        with SessionLocal() as db:
            rows = db.execute(cls.search_statement(db, question, k, user_id, document_ids)).all()
            return [LCDocument(page_content=row.content, metadata={
                **(row.chunk_metadata or {}),
                "document_id": str(row.document_id), "chunk_id": str(row.id),
                "chunk_index": row.chunk_index, "document_name": row.original_filename,
                "filename": row.original_filename, "bm25_score": float(row.score),
                "source": "postgres_full_text",
            }) for row in rows]
