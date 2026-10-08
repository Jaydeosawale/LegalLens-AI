"""
=========================================================
LegalLens AI
EasyOCR Provider
=========================================================
"""

from __future__ import annotations

from pathlib import Path
import threading

import easyocr


class EasyOCRProvider:
    """
    Singleton EasyOCR Provider.
    """

    _reader = None

    @classmethod
    def get_reader(cls):

        if cls._reader is None:

            print("=" * 80)
            print("LOADING EASYOCR")
            print("=" * 80)

            cls._reader = easyocr.Reader(
                ["en"],
                gpu=False,
            )

            print("EasyOCR Ready")
            print("=" * 80)

        return cls._reader

    @classmethod
    def extract_text(cls, image_path):

        image_path = Path(image_path)

        if not image_path.exists():

            raise FileNotFoundError(
                f"Image not found:\n{image_path.resolve()}"
            )

        print("=" * 80)
        print("EASYOCR")
        print("=" * 80)

        print("Thread :", threading.current_thread().name)
        print("Image  :", image_path)

        reader = cls.get_reader()

        # --------------------------------------------------
        # OCR
        # --------------------------------------------------

        results = reader.readtext(
            str(image_path),
            detail=1,

        )

        blocks = []
        lines = []

        for result in results:

            try:

                bbox, text, confidence = result

                text = text.strip()

                if not text:
                    continue

                blocks.append(
                    {
                        "text": text,
                        "confidence": float(confidence),
                        "bbox": bbox,
                    }
                )

                lines.append(text)

            except Exception:
                continue

        full_text = "\n".join(lines)

        print("=" * 80)
        print("OCR SUMMARY")
        print("=" * 80)

        print("Detected Blocks :", len(blocks))
        print("Characters      :", len(full_text))

        if blocks:

            print("\nTop OCR Results\n")

            for i, block in enumerate(blocks[:5], start=1):

                print(f"Block {i}")

                print(
                    "Confidence :",
                    f"{block['confidence']:.3f}",
                )

                print(
                    "Text :",
                    block["text"][:150],
                )

                print("-" * 60)

        else:

            print("No text detected.")

        print("=" * 80)

        # Future:
        # return {
        #     "text": full_text,
        #     "blocks": blocks,
        # }

        return full_text