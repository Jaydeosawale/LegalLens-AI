"""
=========================================================
LegalLens AI
PostgreSQL + pgvector Retriever
=========================================================

Performs semantic similarity search using:

    Question
        ↓
    SentenceTransformer Embedding
        ↓
    PostgreSQL pgvector
        ↓
    Cosine Similarity Search
        ↓
    LangChain Documents
"""

from langchain_core.documents import Document
from sqlalchemy import text
from sqlalchemy.orm import Session

from api.database.database import SessionLocal
from rag.embeddings.embeddings import EmbeddingModel
from api.core.document_access import rag_document_query


class PostgresVectorRetriever:

    @staticmethod
    def retrieve(
        question: str,
        k: int = 8,
        db: Session | None = None,
        user_id=None,
        document_ids=None,
    ) -> list[Document]:
        """
        Retrieve the most semantically relevant document
        chunks using PostgreSQL + pgvector.
        """
        if not user_id:
            return []

        print("\n" + "=" * 80)
        print("POSTGRESQL PGVECTOR RETRIEVER")
        print("=" * 80)

        print("Question:", question)
        print("Top K:", k)

        # --------------------------------------------------
        # 1. Generate query embedding
        # --------------------------------------------------

        print("\nGenerating query embedding...")

        embedding_model = EmbeddingModel.get_model()

        query_embedding = embedding_model.embed_query(
            question
        )

        print(
            "Embedding dimension:",
            len(query_embedding),
        )

        # --------------------------------------------------
        # 2. Create database session if needed
        # --------------------------------------------------

        owns_session = False

        if db is None:

            db = SessionLocal()
            owns_session = True

        try:
            allowed_ids = [str(document.id) for document in rag_document_query(db, user_id, document_ids).all()]
            if not allowed_ids:
                return []

            # --------------------------------------------------
            # 3. pgvector similarity search
            # --------------------------------------------------

            print("\nSearching PostgreSQL pgvector...")

            vector_string = (
                "["
                + ",".join(
                    str(value)
                    for value in query_embedding
                )
                + "]"
            )

            query = text("""
                SELECT
                    dc.id AS chunk_id,
                    dc.document_id,
                    dc.chunk_index,
                    dc.content,
                    dc.metadata,
                    d.original_filename,
                    d.file_type,
                    d.created_at,
                    1 - (
                        de.embedding
                        <=> CAST(:embedding AS vector)
                    ) AS similarity
                FROM document_embeddings de
                JOIN document_chunks dc
                    ON de.chunk_id = dc.id
                JOIN documents d
                    ON dc.document_id = d.id
                WHERE d.processing_status = 'completed'
                  AND d.approval_status = 'approved'
                  AND d.access_enabled = true
                  AND CAST(d.id AS text) = ANY(:document_ids)
                ORDER BY
                    de.embedding
                    <=> CAST(:embedding AS vector)
                LIMIT :k
            """)

            result = db.execute(
                query,
                {
                    "embedding": vector_string,
                    "k": k,
                    "user_id": user_id,
                    "all_documents": document_ids is None,
                    "document_ids": allowed_ids,
                },
            )

            rows = result.mappings().all()

            print(
                "Retrieved chunks:",
                len(rows),
            )

            # --------------------------------------------------
            # 4. Convert database rows to LangChain Documents
            # --------------------------------------------------

            documents = []

            for row in rows:

                metadata = row["metadata"] or {}

                metadata = {
                    **metadata,

                    "chunk_id": str(
                        row["chunk_id"]
                    ),

                    "document_id": str(
                        row["document_id"]
                    ),

                    "chunk_index": row["chunk_index"],

                    "document_name": (
                        row["original_filename"]
                    ),

                    "filename": (
                        row["original_filename"]
                    ),

                    "file_type": (
                        row["file_type"]
                    ),

                    "similarity": float(
                        row["similarity"]
                    ),
                }

                document = Document(
                    page_content=row["content"],
                    metadata=metadata,
                )

                documents.append(document)

            # --------------------------------------------------
            # 5. Debug preview
            # --------------------------------------------------

            print("\nRETRIEVED DOCUMENTS")

            for index, document in enumerate(
                documents[:3],
                start=1,
            ):

                print("\n" + "-" * 60)

                print(
                    f"DOCUMENT {index}"
                )

                print(
                    "File:",
                    document.metadata.get(
                        "document_name"
                    ),
                )

                print(
                    "Chunk:",
                    document.metadata.get(
                        "chunk_index"
                    ),
                )

                print(
                    "Similarity:",
                    document.metadata.get(
                        "similarity"
                    ),
                )

                preview = (
                    document.page_content[:250]
                    .replace("\n", " ")
                    .strip()
                )

                print(
                    "Preview:",
                    preview,
                )

            print("\n" + "=" * 80)
            print("POSTGRESQL RETRIEVAL COMPLETE")
            print("=" * 80)

            return documents

        finally:

            if owns_session:

                db.close()
