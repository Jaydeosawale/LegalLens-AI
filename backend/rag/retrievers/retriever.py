"""
=========================================================
LegalLens AI
Retriever Service
Deep Debug Version
=========================================================
"""

from __future__ import annotations

import threading
import time
import traceback

import numpy as np

from rag.embeddings.embeddings import EmbeddingModel


class RetrieverService:
    """
    Direct FAISS Retriever

    This version bypasses LangChain similarity_search()
    so we can determine whether the problem is:

    1. Embedding generation
    2. FAISS search
    3. LangChain wrapper
    """

    @staticmethod
    def retrieve(
        vector_db,
        question: str,
        search_type: str = "similarity",
        k: int = 6,
    ):

        if vector_db is None:
            raise ValueError(
                "Vector database is not initialized."
            )

        print("\n" + "=" * 80)
        print("DIRECT FAISS DEBUG")
        print("=" * 80)

        print("Question      :", question)
        print("Top K         :", k)
        print("Thread        :", threading.current_thread().name)
        print("Vector DB ID  :", id(vector_db))
        print("Index Size    :", vector_db.index.ntotal)

        try:

            # =====================================================
            # STEP 1 : Generate Embedding
            # =====================================================

            print("\nSTEP 1 : GENERATING QUERY EMBEDDING")
            import inspect

            print("EmbeddingModel file:")
            print(inspect.getfile(EmbeddingModel))

            model = EmbeddingModel.get_model()

            print("Model class:", type(model))
            print("embed_query implementation:", model.embed_query)

            start = time.time()

            embedding = EmbeddingModel.get_model().embed_query(
                question
            )

            print(
                f"Embedding generated in {time.time() - start:.3f} sec"
            )

            print(
                "Embedding Length:",
                len(embedding),
            )

            # =====================================================
            # STEP 2 : Raw FAISS Search
            # =====================================================

            print("\nSTEP 2 : RAW FAISS SEARCH")

            start = time.time()

            scores, indices = vector_db.index.search(
                np.array([embedding], dtype="float32"),
                k,
            )

            print(
                f"FAISS search completed in {time.time() - start:.3f} sec"
            )

            print("Scores :", scores)
            print("Indices:", indices)

            # =====================================================
            # STEP 3 : Convert Index -> Documents
            # =====================================================

            print("\nSTEP 3 : CONVERT TO DOCUMENTS")

            docs = []

            for idx in indices[0]:

                if idx == -1:
                    continue

                doc_id = vector_db.index_to_docstore_id[idx]

                doc = vector_db.docstore.search(doc_id)

                docs.append(doc)

            print(
                f"Retrieved {len(docs)} documents"
            )

            # =====================================================
            # Preview
            # =====================================================

            for i, doc in enumerate(docs[:3], start=1):

                print("\n" + "-" * 60)
                print(f"DOCUMENT {i}")

                print(
                    "File :",
                    doc.metadata.get(
                        "document_name",
                        doc.metadata.get(
                            "filename",
                            "Unknown",
                        ),
                    ),
                )

                print(
                    "Page :",
                    doc.metadata.get(
                        "page",
                        "-",
                    ),
                )

                preview = (
                    doc.page_content[:200]
                    .replace("\n", " ")
                    .strip()
                )

                print(preview)

            print("\nDIRECT FAISS DEBUG COMPLETE")

            return docs

        except Exception:

            print("\n" + "=" * 80)
            print("RETRIEVER FAILED")
            print("=" * 80)

            traceback.print_exc()

            raise