"""
=========================================================
LegalLens AI
OCR Router
=========================================================
"""

from rag.ocr.easyocr_provider import EasyOCRProvider


class OCRRouter:
    """
    Routes OCR requests to the selected provider.
    """

    DEFAULT_PROVIDER = "easyocr"

    @classmethod
    def extract_text(
        cls,
        image_path,
        provider=None,
    ):

        provider = (
            provider
            or cls.DEFAULT_PROVIDER
        ).lower()

        if provider == "easyocr":

            return EasyOCRProvider.extract_text(
                image_path
            )

        raise ValueError(
            f"Unsupported OCR provider: {provider}"
        )