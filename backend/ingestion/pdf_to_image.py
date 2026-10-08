"""
=========================================================
LegalLens AI
PDF To Image
=========================================================
"""

from __future__ import annotations

from pathlib import Path

from pdf2image import convert_from_path


class PDFToImage:
    """
    Converts PDF pages into images.

    Enterprise Features

    ✓ Converts only once
    ✓ Reuses existing images
    ✓ Shared by OCR & Image Search
    """

    IMAGE_ROOT = Path("data") / "pdf_images"

    # =====================================================
    # Folder
    # =====================================================

    @classmethod
    def get_output_folder(
        cls,
        pdf_path,
    ):

        pdf_path = Path(pdf_path)

        folder = (
            cls.IMAGE_ROOT
            / pdf_path.stem
        )

        folder.mkdir(
            parents=True,
            exist_ok=True,
        )

        return folder

    # =====================================================
    # Existing Images
    # =====================================================

    @staticmethod
    def existing_images(
        folder,
    ):

        images = sorted(
            folder.glob("page_*.jpg")
        )

        return images

    # =====================================================
    # Convert
    # =====================================================

    @classmethod
    def convert(
        cls,
        pdf_path,
        dpi=300,
        image_format="JPEG",
    ):

        pdf_path = Path(pdf_path)

        output_folder = cls.get_output_folder(
            pdf_path
        )

        # --------------------------------------------------
        # Cache
        # --------------------------------------------------

        cached = cls.existing_images(
            output_folder
        )

        if cached:

            print("=" * 80)
            print("PDF IMAGES FOUND")
            print(pdf_path.name)
            print("Pages :", len(cached))
            print("=" * 80)

            return cached

        # --------------------------------------------------
        # Convert
        # --------------------------------------------------

        print("=" * 80)
        print("CONVERTING PDF TO IMAGES")
        print(pdf_path.name)
        print("=" * 80)

        pages = convert_from_path(
            str(pdf_path),
            dpi=dpi,
        )

        image_paths = []

        for index, page in enumerate(
            pages,
            start=1,
        ):

            image_path = (
                output_folder
                / f"page_{index}.jpg"
            )

            page.save(
                image_path,
                image_format,
            )

            image_paths.append(
                image_path
            )

        print("Pages :", len(image_paths))

        print("=" * 80)

        return image_paths

    # =====================================================
    # Delete Images
    # =====================================================

    @classmethod
    def delete(
        cls,
        pdf_name,
    ):

        folder = (
            cls.IMAGE_ROOT
            / Path(pdf_name).stem
        )

        if not folder.exists():

            return

        for image in folder.glob("*"):

            image.unlink()

        folder.rmdir()

        print("=" * 80)
        print("PDF IMAGE CACHE REMOVED")
        print(pdf_name)
        print("=" * 80)