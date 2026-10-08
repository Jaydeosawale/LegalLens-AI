"""
=========================================================
LegalLens AI
Enterprise Image Similarity Service
=========================================================
"""

from pathlib import Path

from api.vision.image_embedding_service import (
    ImageEmbeddingService,
)
from api.vision.image_search_service import (
    ImageSearchService,
)


class ImageSimilarityService:
    """
    Enterprise Image Similarity Service.

    Responsibilities

    ✓ Image → Image Search

    Notes

    • Uses the shared ImageVectorStore.
    • Does not own a FAISS index.
    • StartupManager initializes everything.
    """

    # =====================================================
    # Image → Image
    # =====================================================

    @staticmethod
    def search(
        image_path,
        k=5,
        min_score=0.20,
    ):



        import inspect
        from rag.vectorstore.image_vector_store import ImageVectorStore

        print("=" * 80)
        print("SIMILARITY USING")
        print(inspect.getfile(ImageVectorStore))
        print("=" * 80)
        image_path = Path(image_path)

        if not image_path.exists():

            raise FileNotFoundError(
                image_path
            )

        print("=" * 80)
        print("IMAGE SIMILARITY SEARCH")
        print("=" * 80)

        print(
            "Image :",
            image_path.name,
        )

        embedding = ImageEmbeddingService.embed_image(
            image_path
        )

        results = ImageSearchService.search_embedding(
            embedding=embedding,
            k=k,
            min_score=min_score,
        )

        print(
            "Matches :",
            len(results),
        )

        print("=" * 80)

        return results

    # =====================================================
    # Embedding → Image
    # =====================================================

    @staticmethod
    def search_by_embedding(
        embedding,
        k=5,
        min_score=0.20,
    ):

        return ImageSearchService.search_embedding(
            embedding=embedding,
            k=k,
            min_score=min_score,
        )

    # =====================================================
    # Statistics
    # =====================================================

    @staticmethod
    def stats():

        return ImageSearchService.stats()

    # =====================================================
    # Health
    # =====================================================

    @staticmethod
    def health():

        return ImageSearchService.health()