"""
=========================================================
LegalLens AI
Production Hybrid Retriever
=========================================================

Pipeline:

1. Multi Query Generation
2. Query Selection
3. PostgreSQL pgvector Semantic Search
4. PostgreSQL BM25 Keyword Search
5. Reciprocal Rank Fusion
6. Cross Encoder Reranking
"""

import traceback

from api.services.postgres_bm25 import PostgresBM25Retriever

from rag.retrievers.multi_query import MultiQueryGenerator
from rag.retrievers.postgres_vector_retriever import (
    PostgresVectorRetriever,
)
from rag.retrievers.query_selector import QuerySelector
from rag.retrievers.rank_fusion import ReciprocalRankFusion
from rag.reranker.reranker import Reranker


class HybridRetriever:

    @staticmethod
    def retrieve(
        question: str,
        k: int = 5,
        user_id=None,
        document_ids=None,
    ):

        print()
        print("=" * 80)
        print("LEGAL LENS HYBRID RETRIEVER")
        print("=" * 80)

        print("Question:", question)
        print("Final Top K:", k)

        # =====================================================
        # 1. MULTI QUERY GENERATION
        # =====================================================

        print()
        print("=" * 80)
        print("MULTI QUERY GENERATION")
        print("=" * 80)

        queries = MultiQueryGenerator.generate(
            question
        )

        # =====================================================
        # 2. QUERY SELECTION
        # =====================================================

        queries = QuerySelector.select(
            queries,
            max_queries=3,
        )

        print()
        print("Selected Queries:")

        for i, query in enumerate(
            queries,
            start=1,
        ):
            print(f"{i}. {query}")

        # =====================================================
        # RETRIEVAL RESULTS
        # =====================================================

        all_pgvector = []
        all_bm25 = []

        # =====================================================
        # 3. SEARCH EACH QUERY
        # =====================================================

        for index, query in enumerate(
            queries,
            start=1,
        ):

            print()
            print("=" * 80)
            print(f"QUERY {index}")
            print("=" * 80)

            print(query)

            # -------------------------------------------------
            # PGVECTOR SEARCH
            # -------------------------------------------------

            print()
            print("Running PostgreSQL pgvector...")

            try:

                pgvector_docs = (
                    PostgresVectorRetriever.retrieve(
                        question=query,
                        k=k,
                        user_id=user_id,
                        document_ids=document_ids,
                    )
                )

                print(
                    "pgvector results:",
                    len(pgvector_docs),
                )

                all_pgvector.extend(
                    pgvector_docs
                )

            except Exception:

                print()
                print("PGVECTOR SEARCH FAILED")

                traceback.print_exc()

                raise

            # -------------------------------------------------
            # BM25 SEARCH
            # -------------------------------------------------

            print()
            print("Running PostgreSQL BM25...")

            try:

                bm25_docs = (
                    PostgresBM25Retriever.retrieve(
                        question=query,
                        k=k,
                        user_id=user_id,
                        document_ids=document_ids,
                    )
                )

                print(
                    "BM25 results:",
                    len(bm25_docs),
                )

                all_bm25.extend(
                    bm25_docs
                )

            except Exception:

                print()
                print("BM25 SEARCH FAILED")

                traceback.print_exc()

                raise

        # =====================================================
        # 4. RETRIEVAL SUMMARY
        # =====================================================

        print()
        print("=" * 80)
        print("HYBRID RETRIEVAL SUMMARY")
        print("=" * 80)

        print(
            "Total pgvector results:",
            len(all_pgvector),
        )

        print(
            "Total BM25 results:",
            len(all_bm25),
        )

        # =====================================================
        # 5. RECIPROCAL RANK FUSION
        # =====================================================

        print()
        print("=" * 80)
        print("RUNNING RRF")
        print("=" * 80)

        try:

            merged_docs = (
                ReciprocalRankFusion.fuse(
                    rankings=[
                        all_pgvector,
                        all_bm25,
                    ],
                    top_k=k * 3,
                )
            )

            print(
                "RRF documents:",
                len(merged_docs),
            )

        except Exception:

            print()
            print("RRF FAILED")

            traceback.print_exc()

            raise

        # =====================================================
        # 6. CROSS ENCODER RERANKING
        # =====================================================

        print()
        print("=" * 80)
        print("RUNNING CROSS ENCODER RERANKER")
        print("=" * 80)

        try:

            reranked_docs = Reranker.rerank(
                question=question,
                documents=merged_docs,
                top_k=k,
            )

            print()
            print(
                "Final reranked documents:",
                len(reranked_docs),
            )

            print()
            print("=" * 80)
            print("HYBRID RETRIEVAL COMPLETE")
            print("=" * 80)

            return reranked_docs

        except Exception:

            print()
            print("CROSS ENCODER FAILED")

            traceback.print_exc()

            print()
            print(
                "Returning RRF fallback results"
            )

            return merged_docs[:k]
