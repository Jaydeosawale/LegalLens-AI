"""
=========================================================
LegalLens AI
Enterprise Vision Pipeline
=========================================================
"""

from __future__ import annotations

from api.vision.image_search_service import (
    ImageSearchService,
)
from api.vision.image_similarity_service import (
    ImageSimilarityService,
)
from rag.ocr.ocr_service import OCRService


class VisionPipeline:
    """
    Enterprise Vision Pipeline.

    Responsibilities

    ✓ Text → Image Retrieval
    ✓ Image → Image Retrieval
    ✓ OCR
    ✓ Future Image Generation
    ✓ Future Vision LLM

    This class only orchestrates services.
    """

    IMAGE_KEYWORDS = {

        "image",
        "photo",
        "picture",
        "figure",
        "diagram",
        "graph",
        "chart",
        "table",
        "map",
        "logo",
        "stamp",
        "seal",
        "signature",
        "drawing",

    }

    # =====================================================
    # Should Search Images
    # =====================================================

    @classmethod
    def need_image_search(
        cls,
        question,
        uploaded_image=None,
    ):

        if uploaded_image:

            return True

        question = question.lower()

        return any(

            keyword in question

            for keyword in cls.IMAGE_KEYWORDS

        )

    # =====================================================
    # Main Pipeline
    # =====================================================

    @classmethod
    def process(

        cls,

        question,

        search_query,

        uploaded_image=None,

        image_k=5,

    ):

        image_results = []

        similar_images = []

        image_analysis = None

        # --------------------------------------------------
        # Text → Image
        # --------------------------------------------------

        if cls.need_image_search(

            question,

            uploaded_image,

        ):

            try:

                image_results = ImageSearchService.search_text(

                    query=search_query,

                    k=image_k,

                )

                print("=" * 80)
                print("TEXT → IMAGE")
                print("Images :", len(image_results))
                print("=" * 80)

            except Exception as e:

                print("=" * 80)
                print("TEXT → IMAGE FAILED")
                print(e)
                print("=" * 80)

        # --------------------------------------------------
        # Image → Image
        # --------------------------------------------------

        if uploaded_image:

            try:

                similar_images = ImageSimilarityService.search(

                    uploaded_image,

                    k=image_k,

                )

                print("=" * 80)
                print("IMAGE → IMAGE")
                print("Matches :", len(similar_images))
                print("=" * 80)

            except Exception as e:

                print("=" * 80)
                print("IMAGE → IMAGE FAILED")
                print(e)
                print("=" * 80)

        # --------------------------------------------------
        # OCR
        # --------------------------------------------------

        if uploaded_image:

            try:

                image_analysis = OCRService.extract(

                    uploaded_image

                )

                print("=" * 80)
                print("OCR COMPLETE")
                print("=" * 80)

            except Exception as e:

                print("=" * 80)
                print("OCR FAILED")
                print(e)
                print("=" * 80)

        return {

            "image_results": image_results,

            "similar_images": similar_images,

            "image_analysis": image_analysis,

        }

    # =====================================================
    # Statistics
    # =====================================================

    @staticmethod
    def stats():

        return {

            "image_store":
                ImageSearchService.stats(),

            "similarity":
                ImageSimilarityService.stats(),

        }

    # =====================================================
    # Health
    # =====================================================

    @staticmethod
    def health():

        return {

            "image_store":
                ImageSearchService.health(),

            "similarity":
                ImageSimilarityService.health(),

        }