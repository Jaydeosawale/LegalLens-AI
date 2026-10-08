from collections import defaultdict


class ReciprocalRankFusion:
    """
    Reciprocal Rank Fusion (RRF)

    Combines multiple ranked retrieval results into a
    single ranking while removing duplicate document chunks.

    LegalLens retrieval sources currently include:

    - PostgreSQL pgvector semantic search
    - PostgreSQL BM25 keyword search
    """

    K = 60

    @staticmethod
    def _document_key(doc):
        """
        Generate a stable key for document deduplication.

        Priority:

        1. chunk_id
        2. document_id + chunk_index
        3. filename + page
        4. filename + content hash
        """

        metadata = doc.metadata

        # Best identifier:
        # PostgreSQL chunk UUID
        chunk_id = metadata.get("chunk_id")

        if chunk_id:
            return (
                "chunk",
                str(chunk_id),
            )

        # Secondary identifier
        document_id = metadata.get("document_id")
        chunk_index = metadata.get("chunk_index")

        if (
            document_id is not None
            and chunk_index is not None
        ):
            return (
                "document_chunk",
                str(document_id),
                int(chunk_index),
            )

        # Filename
        filename = (
            metadata.get("document_name")
            or metadata.get("filename")
            or ""
        )

        # Page fallback
        page = (
            metadata.get("page_number")
            or metadata.get("page")
        )

        if page is not None:
            return (
                "page",
                filename,
                page,
            )

        # Final fallback
        return (
            "content",
            filename,
            hash(doc.page_content),
        )

    @staticmethod
    def fuse(
        rankings,
        top_k=10,
    ):

        scores = defaultdict(float)
        documents = {}

        for ranking in rankings:

            for rank, doc in enumerate(
                ranking,
                start=1,
            ):

                key = (
                    ReciprocalRankFusion
                    ._document_key(doc)
                )

                # Reciprocal Rank Fusion formula
                scores[key] += 1 / (
                    ReciprocalRankFusion.K + rank
                )

                # Keep the first document instance
                if key not in documents:
                    documents[key] = doc

        ranked_results = sorted(
            scores.items(),
            key=lambda item: item[1],
            reverse=True,
        )

        fused_docs = []

        for key, score in ranked_results[:top_k]:

            document = documents[key]

            # Store RRF score for debugging
            document.metadata["rrf_score"] = float(
                score
            )

            fused_docs.append(
                document
            )

        print()
        print("=" * 80)
        print("RECIPROCAL RANK FUSION")
        print("=" * 80)
        print(
            "Unique documents:",
            len(fused_docs),
        )
        print("=" * 80)

        return fused_docs