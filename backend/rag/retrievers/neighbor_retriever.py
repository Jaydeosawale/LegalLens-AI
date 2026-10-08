"""
=========================================================
LegalLens AI
PostgreSQL Neighbor Retriever
=========================================================

Expands retrieved chunks with their previous and next
chunks from the same document.

Important behavior:

- Original retrieved documents preserve all ranking metadata.
- Newly added neighbor chunks receive neighbor metadata.
- Uses PostgreSQL instead of the old local FAISS/vector_db.
"""

from sqlalchemy import and_
from sqlalchemy.orm import joinedload

from api.database.database import SessionLocal
from api.models.document_chunk import DocumentChunk
from api.models.document import Document


class NeighborRetriever:
    """
    PostgreSQL Neighbor Retriever.

    For every retrieved chunk:

        Previous Chunk
              │
              ▼
        Current Chunk
              │
              ▼
          Next Chunk

    Original retrieved chunks keep their metadata.

    New neighbor chunks are loaded from PostgreSQL using:

        document_id
        chunk_index
    """

    @staticmethod
    def expand(documents):

        if not documents:
            return []

        print()
        print("=" * 80)
        print("POSTGRESQL NEIGHBOR EXPANSION")
        print("=" * 80)

        print(
            "Input Documents:",
            len(documents),
        )

        db = SessionLocal()

        try:

            expanded = []
            seen = set()

            # =================================================
            # First preserve original retrieved documents
            # =================================================

            original_chunks = {}

            for document in documents:

                metadata = document.metadata

                document_id = metadata.get(
                    "document_id"
                )

                chunk_index = metadata.get(
                    "chunk_index"
                )

                if (
                    document_id is None
                    or chunk_index is None
                ):

                    key = (
                        "original",
                        id(document),
                    )

                    if key not in seen:

                        seen.add(key)
                        expanded.append(document)

                    continue

                key = (
                    str(document_id),
                    chunk_index,
                )

                if key not in seen:

                    seen.add(key)

                    # Preserve original document completely.
                    # This keeps:
                    #
                    # rrf_score
                    # reranker_score
                    # similarity score
                    # bm25 score
                    # source metadata
                    #
                    expanded.append(document)

                    original_chunks[key] = document

            # =================================================
            # Retrieve previous and next neighbors
            # =================================================

            for document in documents:

                metadata = document.metadata

                document_id = metadata.get(
                    "document_id"
                )

                chunk_index = metadata.get(
                    "chunk_index"
                )

                if (
                    document_id is None
                    or chunk_index is None
                ):
                    continue

                start_index = max(
                    0,
                    chunk_index - 1,
                )

                end_index = (
                    chunk_index + 1
                )

                neighbours = (

                    db.query(DocumentChunk)

                    .options(
                        joinedload(
                            DocumentChunk.document
                        )
                    )

                    .join(
                        Document,
                        DocumentChunk.document_id
                        == Document.id,
                    )

                    .filter(
                        and_(
                            DocumentChunk.document_id
                            == document_id,

                            DocumentChunk.chunk_index
                            >= start_index,

                            DocumentChunk.chunk_index
                            <= end_index,

                            Document.processing_status
                            == "completed",
                            Document.approval_status == "approved",
                            Document.access_enabled.is_(True),
                        )
                    )

                    .order_by(
                        DocumentChunk.chunk_index
                    )

                    .all()
                )

                # =================================================
                # Add only NEW neighbor chunks
                # =================================================

                from langchain_core.documents import (
                    Document as LCDocument,
                )

                for chunk in neighbours:

                    neighbour_key = (
                        str(chunk.document_id),
                        chunk.chunk_index,
                    )

                    # Original retrieved chunk already exists.
                    # Do not replace it.
                    if neighbour_key in seen:
                        continue

                    seen.add(neighbour_key)

                    db_document = chunk.document

                    expanded.append(

                        LCDocument(

                            page_content=chunk.content,

                            metadata={

                                "document_id": str(
                                    db_document.id
                                ),

                                "chunk_id": str(
                                    chunk.id
                                ),

                                "chunk_index":
                                    chunk.chunk_index,

                                "document_name":
                                    db_document.original_filename,

                                "source":
                                    "postgres_neighbor",

                                "neighbor_expanded":
                                    True,

                            },

                        )

                    )

            print()

            print(
                "Expanded Documents:",
                len(expanded),
            )

            print("=" * 80)
            print(
                "NEIGHBOR EXPANSION COMPLETE"
            )
            print("=" * 80)

            return expanded

        except Exception as error:

            print()

            print(
                "Neighbor Retriever Error:",
                error,
            )

            print(
                "Returning original documents."
            )

            return documents

        finally:

            db.close()
