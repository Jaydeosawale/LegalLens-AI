"""
=========================================================
LegalLens AI
Text Normalizer
=========================================================
"""

from __future__ import annotations

import html
import re

from .unicode_normalizer import UnicodeNormalizer


class TextNormalizer:
    """
    Normalize text while preserving
    meaningful legal punctuation.
    """

    @staticmethod
    def normalize(
        text: str,
    ) -> str:

        if not text:

            return ""

        # Unicode normalization
        text = UnicodeNormalizer.normalize(text)

        # Decode HTML entities
        text = html.unescape(text)

        # Lowercase
        text = text.lower()

        # Remove zero-width characters
        text = re.sub(
            r"[\u200B-\u200D\uFEFF]",
            "",
            text,
        )

        # Normalize whitespace
        text = re.sub(
            r"\s+",
            " ",
            text,
        )

        # Preserve:
        # letters
        # digits
        # hyphen
        # slash
        # colon
        # dot

        text = re.sub(
            r"[^a-z0-9\s\-/.:]",
            " ",
            text,
        )

        # Remove duplicated spaces
        text = re.sub(
            r"\s+",
            " ",
            text,
        )

        return text.strip()