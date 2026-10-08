"""
=========================================================
LegalLens AI
OCR Service
=========================================================
"""

from rag.ocr.ocr_router import OCRRouter


class OCRService:
    """
    Public OCR API.
    """

    @staticmethod
    def extract(
        image_path,
        provider=None,
    ):

        return OCRRouter.extract_text(
            image_path=image_path,
            provider=provider,
        )