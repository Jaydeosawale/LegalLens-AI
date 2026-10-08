"""
=========================================================
LegalLens AI
BM25 Retriever Service
=========================================================
"""

from api.services.bm25_index import BM25Index


class BM25RetrieverService:
    """
    Uses the persistent BM25 index.
    """

    @staticmethod
    def retrieve(query, k=6):

        if BM25Index.size() == 0:

            print("=" * 80)
            print("BM25 INDEX EMPTY")
            print("=" * 80)

            return []

        return BM25Index.search(
            query=query,
            k=k,
        )