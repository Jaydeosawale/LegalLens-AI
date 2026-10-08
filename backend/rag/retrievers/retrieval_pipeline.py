"""
=========================================================
LegalLens AI
Retrieval Pipeline
=========================================================

Central PostgreSQL-based retrieval pipeline.
"""

from core.utils.document_utils import DocumentUtils
from api.services.system_settings_service import get_system_settings

from rag.retrievers.context_compressor import ContextCompressor
from rag.retrievers.hybrid_retriever import HybridRetriever
from rag.retrievers.neighbor_retriever import NeighborRetriever
from rag.retrievers.query_analyzer import QueryAnalyzer
from rag.retrievers.score_filter import ScoreFilter


class RetrievalPipeline:
    """
    Central Retrieval Pipeline

    Pipeline

        Query
          │
          ▼
    Query Analyzer
          │
          ▼
    Hybrid Retriever
          │
          ▼
    Score Filter
          │
          ▼
    Duplicate Removal
          │
          ▼
    Neighbor Expansion
          │
          ▼
    Duplicate Removal
          │
          ▼
    Context Compression
          │
          ▼
    Return Documents
    """

    @staticmethod
    def retrieve(
        question,
        k=8,
        user_id=None,
        document_ids=None,
    ):

        print()
        print("=" * 80)
        print("RETRIEVAL PIPELINE")
        print("=" * 80)

        # ==================================================
        # Query Analysis
        # ==================================================

        analysis = QueryAnalyzer.analyze(question)

        print()
        print("QUERY ANALYSIS")
        print(analysis)

        # ==================================================
        # Hybrid Retrieval
        # ==================================================

        top_k = get_system_settings()['top_k']

        documents = HybridRetriever.retrieve(
            question=question,
            k=top_k,
            user_id=user_id,
            document_ids=document_ids,
        )

        print()
        print(
            "Retrieved Documents:",
            len(documents),
        )

        # ==================================================
        # Score Filter
        # ==================================================

        documents = ScoreFilter.filter(
            documents=documents,
            minimum_score=0.0,
        )

        print(
            "After Score Filter:",
            len(documents),
        )

        # ==================================================
        # Initial Duplicate Removal
        # ==================================================

        documents = DocumentUtils.remove_duplicates(
            documents
        )

        print(
            "After Initial Duplicate Removal:",
            len(documents),
        )

        # ==================================================
        # PostgreSQL Neighbor Expansion
        # ==================================================

        needs_neighbors = analysis.get(
            "needs_neighbors",
            False,
        )

        if needs_neighbors:

            print()
            print(
                "Neighbor Expansion Required"
            )

            documents = NeighborRetriever.expand(
                documents=documents,
            )

            print(
                "After Neighbor Expansion:",
                len(documents),
            )

        else:

            print()
            print(
                "Neighbor Expansion Not Required"
            )

        # ==================================================
        # Duplicate Removal After Neighbor Expansion
        # ==================================================

        documents = DocumentUtils.remove_duplicates(
            documents
        )

        print(
            "After Final Duplicate Removal:",
            len(documents),
        )

        # ==================================================
        # Context Compression
        # ==================================================

        try:

            documents = ContextCompressor.compress(
                question=question,
                documents=documents,
            )

            print(
                "After Context Compression:",
                len(documents),
            )

        except Exception as error:

            print()
            print(
                "Context Compression Skipped"
            )

            print(
                "Reason:",
                error,
            )

        print()
        print("=" * 80)
        print("RETRIEVAL COMPLETE")
        print("=" * 80)

        return documents
