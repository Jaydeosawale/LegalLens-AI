"""
=========================================================
LegalLens AI
Retrieval Manager
=========================================================
"""

from rag.retrievers.hybrid_retriever import HybridRetriever


class RetrievalManager:
    """
    Central retrieval entry point.

    Every retrieval request should come here.

    Current Retrieval Architecture:

        Question
           │
           ▼
    HybridRetriever
           │
     ┌─────┴─────┐
     ▼           ▼
    pgvector    PostgreSQL BM25
     │           │
     └─────┬─────┘
           ▼
          RRF
           │
           ▼
        Reranker
           │
           ▼
        Documents
    """

    @staticmethod
    def retrieve(
        question,
        uploaded_image=None,
        filters=None,
        k=8,
    ):
        """
        Returns ranked documents.
        """

        documents = HybridRetriever.retrieve(
            question=question,
            k=k,
        )

        # Future:
        #
        # if uploaded_image:
        #     documents += ImageRetriever.search(...)
        #
        # if filters:
        #     documents = MetadataFilter.apply(...)
        #
        # documents = CitationFilter(...)
        #
        # documents = ContextCompressor(...)

        return documents