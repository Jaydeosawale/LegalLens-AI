"""
=========================================================
LegalLens AI
PostgreSQL BM25 Retriever
=========================================================

Retrieves completed document chunks from PostgreSQL and
performs BM25 keyword ranking.

This replaces the old persistent local bm25.pkl pipeline.
"""

import re

from langchain_core.documents import Document as LCDocument
from rank_bm25 import BM25Okapi
from sqlalchemy.orm import joinedload

from api.database.database import SessionLocal
from api.models.document import Document
from sqlalchemy import or_
from api.models.document_chunk import DocumentChunk


class PostgresBM25Retriever:
    """
    PostgreSQL-backed BM25 retriever.

    Workflow:

        PostgreSQL document_chunks
                ↓
        Load completed chunks
                ↓
        Tokenize content
                ↓
        Build BM25 index
                ↓
        Keyword search
                ↓
        Return LangChain Documents
    """

    # =====================================================
    # Tokenizer
    # =====================================================

    @staticmethod
    def tokenize(text: str) -> list[str]:
        """Convert text into normalized tokens."""

        return re.findall(
            r"\w+",
            text.lower(),
        )

    # =====================================================
    # Retrieve
    # =====================================================

    @classmethod
    def retrieve(
        cls,
        question: str,
        k: int = 10,
        user_id=None,
        document_ids=None,
    ) -> list[LCDocument]:
        """
        Retrieve the top matching document chunks using BM25.
        """
        if not user_id:
            return []

        print()
        print("=" * 80)
        print("POSTGRESQL BM25 RETRIEVER")
        print("=" * 80)

        print("Question:", question)
        print("Top K:", k)

        db = SessionLocal()

        try:

            # -------------------------------------------------
            # Load completed document chunks from PostgreSQL
            # -------------------------------------------------

            chunks = (
                db.query(DocumentChunk)
                .options(
                    joinedload(
                        DocumentChunk.document
                    )
                )
                .join(
                    Document,
                    DocumentChunk.document_id == Document.id,
                )
                .filter(
                    Document.processing_status == "completed",
                    or_(Document.user_id == user_id, Document.id.in_(document_ids or [])),
                    Document.id.in_(document_ids) if document_ids is not None else True,
                )
                .order_by(
                    DocumentChunk.document_id,
                    DocumentChunk.chunk_index,
                )
                .all()
            )

            print()
            print(
                "Chunks loaded from PostgreSQL:",
                len(chunks),
            )

            if not chunks:

                print()
                print("No chunks found.")

                return []

            # -------------------------------------------------
            # Build BM25 corpus
            # -------------------------------------------------

            corpus = [
                cls.tokenize(chunk.content)
                for chunk in chunks
            ]

            bm25 = BM25Okapi(corpus)

            # -------------------------------------------------
            # Tokenize query
            # -------------------------------------------------

            query_tokens = cls.tokenize(question)

            if not query_tokens:

                print()
                print("Question contains no searchable tokens.")

                return []

            # -------------------------------------------------
            # Calculate BM25 scores
            # -------------------------------------------------

            scores = bm25.get_scores(
                query_tokens
            )

            ranked_results = sorted(
                zip(scores, chunks),
                key=lambda item: item[0],
                reverse=True,
            )

            # -------------------------------------------------
            # Convert to LangChain Documents
            # -------------------------------------------------

            results = []

            for score, chunk in ranked_results:

                # Ignore chunks with no keyword match
                if score <= 0:
                    continue

                document = chunk.document

                results.append(
                    LCDocument(
                        page_content=chunk.content,
                        metadata={
                            "document_id": str(
                                document.id
                            ),
                            "chunk_id": str(
                                chunk.id
                            ),
                            "chunk_index": chunk.chunk_index,
                            "document_name": (
                                document.original_filename
                            ),
                            "bm25_score": float(score),
                            "source": "postgres_bm25",
                        },
                    )
                )

                if len(results) >= k:
                    break

            # -------------------------------------------------
            # Result summary
            # -------------------------------------------------

            print()
            print(
                "BM25 results:",
                len(results),
            )

            print()
            print("=" * 80)
            print("POSTGRESQL BM25 COMPLETE")
            print("=" * 80)

            return results

        finally:

            db.close()
