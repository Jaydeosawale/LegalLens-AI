"""
=========================================================
LegalLens AI
Persistent BM25 Index
=========================================================
"""

from __future__ import annotations

import pickle
import re
from pathlib import Path

from rank_bm25 import BM25Okapi


class BM25Index:
    """
    Singleton persistent BM25 index.

    Saves only the indexed documents.

    BM25 is rebuilt on load because rebuilding is
    extremely fast compared to OCR or embeddings.
    """

    BM25_PATH = Path(
        "services/vectorstore/bm25.pkl"
    )

    _bm25 = None
    _documents = []
    _document_count = 0

    # =====================================================
    # Tokenizer
    # =====================================================

    @staticmethod
    def tokenize(text: str):

        return re.findall(
            r"\w+",
            text.lower(),
        )

    # =====================================================
    # Build
    # =====================================================

    @classmethod
    def build(cls, documents):

        if not documents:

            print("=" * 80)
            print("BM25 BUILD SKIPPED")
            print("No documents.")
            print("=" * 80)

            return

        cls._documents = documents
        cls._document_count = len(documents)

        corpus = [

            cls.tokenize(
                doc.page_content
            )

            for doc in documents

        ]

        cls._bm25 = BM25Okapi(
            corpus
        )

        print("=" * 80)
        print("BM25 INDEX BUILT")
        print("Chunks :", cls._document_count)
        print("=" * 80)

    # =====================================================
    # Save
    # =====================================================

    @classmethod
    def save(cls):

        if not cls._documents:

            return

        cls.BM25_PATH.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with open(
            cls.BM25_PATH,
            "wb",
        ) as file:

            pickle.dump(
                {
                    "documents": cls._documents,
                    "count": cls._document_count,
                },
                file,
            )

        print("=" * 80)
        print("BM25 SAVED")
        print("Path :", cls.BM25_PATH)
        print("=" * 80)

    # =====================================================
    # Load
    # =====================================================

    @classmethod
    def load(cls):

        if not cls.BM25_PATH.exists():

            print("=" * 80)
            print("BM25 CACHE NOT FOUND")
            print("=" * 80)

            return False

        with open(
            cls.BM25_PATH,
            "rb",
        ) as file:

            data = pickle.load(file)

        cls._documents = data["documents"]
        cls._document_count = data["count"]

        corpus = [

            cls.tokenize(
                doc.page_content
            )

            for doc in cls._documents

        ]

        cls._bm25 = BM25Okapi(
            corpus
        )

        print("=" * 80)
        print("BM25 LOADED")
        print("Chunks    :", cls._document_count)
        print("Documents :", len(cls._documents))
        print("=" * 80)

        return True

    # =====================================================
    # Search
    # =====================================================

    @classmethod
    def search(
        cls,
        query,
        k=10,
    ):

        if cls._bm25 is None:

            print("=" * 80)
            print("BM25 NOT INITIALIZED")
            print("=" * 80)

            return []

        tokens = cls.tokenize(
            query
        )

        scores = cls._bm25.get_scores(
            tokens
        )

        ranked = sorted(
            zip(
                scores,
                cls._documents,
            ),
            key=lambda x: x[0],
            reverse=True,
        )

        results = [

            doc

            for score, doc in ranked

            if score > 0

        ]

        print("=" * 80)
        print("BM25 SEARCH")
        print("Query   :", query)
        print("Results :", len(results))
        print("=" * 80)

        return results[:k]

    # =====================================================
    # Delete Cache
    # =====================================================

    @classmethod
    def delete(cls):

        if cls.BM25_PATH.exists():

            cls.BM25_PATH.unlink()

            print("=" * 80)
            print("BM25 CACHE DELETED")
            print("=" * 80)

    # =====================================================
    # Reset
    # =====================================================

    @classmethod
    def reset(cls):

        cls._bm25 = None
        cls._documents = []
        cls._document_count = 0

    # =====================================================
    # Statistics
    # =====================================================

    @classmethod
    def stats(cls):

        return {

            "initialized": cls._bm25 is not None,

            "documents": len(cls._documents),

            "chunks": cls._document_count,

            "cache_exists": cls.BM25_PATH.exists(),

            "cache_path": str(
                cls.BM25_PATH
            ),

        }

    # =====================================================
    # Size
    # =====================================================

    @classmethod
    def size(cls):

        return len(
            cls._documents
        )

    @classmethod
    def is_initialized(cls):

        return cls._bm25 is not None