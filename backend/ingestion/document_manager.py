"""
=========================================================
LegalLens AI
Document Manager
=========================================================
"""

import os
from pathlib import Path

from config.settings import UPLOAD_FOLDER
from ingestion.pdf_to_image import PDFToImage
from api.vision.image_search_service import ImageSearchService


class DocumentManager:

    # =====================================================
    # Upload Folder
    # =====================================================

    @staticmethod
    def get_upload_folder():

        folder = Path(
            UPLOAD_FOLDER
        )

        folder.mkdir(
            parents=True,
            exist_ok=True,
        )

        return folder

    # =====================================================
    # Save PDF
    # =====================================================

    @staticmethod
    def save_pdf(uploaded_file):

        folder = (
            DocumentManager.get_upload_folder()
        )

        file_path = (
            folder
            / uploaded_file.filename
        )

        # ------------------------------------------
        # Already Exists
        # ------------------------------------------

        if file_path.exists():

            print("=" * 80)
            print("PDF ALREADY EXISTS")
            print(file_path.name)
            print("=" * 80)

            return file_path, False

        # ------------------------------------------
        # Save PDF
        # ------------------------------------------

        with open(
            file_path,
            "wb",
        ) as f:

            f.write(
                uploaded_file.file.read()
            )

        print("=" * 80)
        print("PDF SAVED")
        print(file_path.name)
        print("=" * 80)

        # ------------------------------------------
        # Extract Images
        # ------------------------------------------

        image_paths = PDFToImage.convert(
            pdf_path=file_path,
        )

        print(
            "Images :",
            len(image_paths),
        )

        # ------------------------------------------
        # Index Images
        # ------------------------------------------

        try:

            ImageSearchService.index_folder(
                str(
                    image_paths[0].parent
                )
            )

            print("=" * 80)
            print("IMAGE INDEX UPDATED")
            print("=" * 80)

        except Exception as e:

            print("=" * 80)
            print("IMAGE INDEX FAILED")
            print(e)
            print("=" * 80)

        return file_path, True

    # =====================================================
    # Documents
    # =====================================================

    @staticmethod
    def list_documents():

        folder = (
            DocumentManager.get_upload_folder()
        )

        return sorted(
            folder.glob("*.pdf")
        )

    # =====================================================
    # Delete
    # =====================================================

    @staticmethod
    def delete_document(filename):

        file_path = (
            DocumentManager.get_upload_folder()
            / filename
        )

        if file_path.exists():

            file_path.unlink()

        PDFToImage.delete(
            filename
        )

    # =====================================================
    # Size
    # =====================================================

    @staticmethod
    def total_size():

        total = 0

        for pdf in (
            DocumentManager.list_documents()
        ):

            total += os.path.getsize(
                pdf
            )

        return total

    # =====================================================
    # Format Size
    # =====================================================

    @staticmethod
    def format_size(size):

        if size < 1024:

            return f"{size} B"

        if size < 1024 * 1024:

            return (
                f"{size / 1024:.2f} KB"
            )

        return (
            f"{size / (1024 * 1024):.2f} MB"
        )