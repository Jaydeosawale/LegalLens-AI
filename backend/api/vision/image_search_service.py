"""
=========================================================
LegalLens AI
Enterprise Image Search Service
=========================================================
"""

from __future__ import annotations

from rag.vectorstore.image_vector_store import (
    ImageVectorStore,
)


class ImageSearchService:
    """
    Enterprise Image Search Service.

    Responsibilities

    ✓ Text → Image Search
    ✓ Image Indexing
    ✓ Folder Indexing
    ✓ Statistics

    Notes

    • Uses the singleton ImageVectorStore
    • StartupManager initializes the store
    • Does not own an image index
    """

    _store = None

    # =====================================================
    # Store
    # =====================================================

    @classmethod
    def get_store(cls):

     if cls._store is None:

        import inspect
        from rag.vectorstore.image_vector_store import ImageVectorStore

        print("=" * 80)
        print("IMAGE VECTOR STORE FILE")
        print(inspect.getfile(ImageVectorStore))
        print("=" * 80)

        cls._store = ImageVectorStore()

     return cls._store
    # =====================================================
    # Index Image
    # =====================================================

    @classmethod
    def index_image(
        cls,
        image_path,
        pdf_name="",
        page=0,
        caption="",
    ):

        return cls.get_store().add_image(
            image_path=image_path,
            pdf_name=pdf_name,
            page=page,
            caption=caption,
        )

    # =====================================================
    # Index Folder
    # =====================================================

    @classmethod
    def index_folder(
        cls,
        folder_path,
    ):

        return cls.get_store().add_folder(
            folder_path
        )

    # =====================================================
    # Rebuild Folder
    # =====================================================

    @classmethod
    def rebuild_folder(
        cls,
        folder_path,
    ):

        store = cls.get_store()

        store.clear()

        return store.add_folder(
            folder_path
        )

    # =====================================================
    # Text → Image
    # =====================================================

    @classmethod
    def search_text(
        cls,
        query,
        k=5,
        min_score=0.20,
    ):

        return cls.get_store().search_text(
            query=query,
            k=k,
            min_score=min_score,
        )

    # =====================================================
    # Embedding → Image
    # =====================================================

    @classmethod
    def search_embedding(
        cls,
        embedding,
        k=5,
        min_score=0.20,
    ):

        return cls.get_store().search_embedding(
            embedding=embedding,
            k=k,
            min_score=min_score,
        )

    # =====================================================
    # Image Paths
    # =====================================================

    @classmethod
    def get_image_paths(
        cls,
        query,
        k=5,
    ):

        results = cls.search_text(
            query=query,
            k=k,
        )

        return [

            item["image_path"]

            for item in results

        ]

    # =====================================================
    # Count
    # =====================================================

    @classmethod
    def total_images(cls):

        return cls.get_store().count()

    # =====================================================
    # Save
    # =====================================================

    @classmethod
    def save(cls):

        cls.get_store().save()

    # =====================================================
    # Clear
    # =====================================================

    @classmethod
    def clear(cls):

        cls.get_store().clear()

    # =====================================================
    # Health
    # =====================================================

    @classmethod
    def health(cls):

        return cls.get_store().health_check()

    # =====================================================
    # Statistics
    # =====================================================

    @classmethod
    def stats(cls):

        return cls.get_store().stats()