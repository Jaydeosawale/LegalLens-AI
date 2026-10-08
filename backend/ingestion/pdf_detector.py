"""
=========================================================
LegalLens AI
PDF Detector
=========================================================
"""

from pathlib import Path

import fitz  # PyMuPDF


class PDFDetector:
    """
    Detects whether a PDF contains extractable text.

    Returns:
        True  -> Digital PDF
        False -> Scanned PDF
    """

    MIN_TEXT_LENGTH = 100
    MAX_PAGES_TO_CHECK = 5

    @classmethod
    def has_text(
        cls,
        pdf_path,
    ):

        pdf_path = Path(pdf_path)

        print("=" * 80)
        print("PDF DETECTOR")
        print("=" * 80)

        print("PDF :", pdf_path.name)

        try:

            document = fitz.open(
                str(pdf_path)
            )

            total_characters = 0

            pages_to_check = min(
                len(document),
                cls.MAX_PAGES_TO_CHECK,
            )

            for page_number in range(
                pages_to_check
            ):

                page = document.load_page(
                    page_number
                )

                text = page.get_text()

                total_characters += len(
                    text.strip()
                )

                if (
                    total_characters
                    >= cls.MIN_TEXT_LENGTH
                ):

                    print(
                        "Digital PDF : True"
                    )

                    print(
                        "Characters :",
                        total_characters,
                    )

                    print("=" * 80)

                    document.close()

                    return True

            document.close()

            print(
                "Digital PDF : False"
            )

            print(
                "Characters :",
                total_characters,
            )

            print("=" * 80)

            return False

        except Exception as e:

            print("=" * 80)
            print("PDF DETECTION FAILED")
            print(e)
            print("=" * 80)

            return False