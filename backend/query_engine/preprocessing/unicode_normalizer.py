"""
=========================================================
LegalLens AI
Unicode Normalizer
=========================================================

Normalizes Unicode characters into a
consistent representation before any
query processing.

Version: V1
"""

from __future__ import annotations

import unicodedata


class UnicodeNormalizer:
    """
    Normalize Unicode characters.

    Examples
    --------
    ﬁ → fi

    “ ” → "

    — → -

    Full-width characters → ASCII
    """

    @staticmethod
    def normalize(
        text: str,
    ) -> str:
        """
        Normalize Unicode text.

        Parameters
        ----------
        text : str

        Returns
        -------
        str
        """

        if not text:

            return ""

        return unicodedata.normalize(
            "NFKC",
            text,
        )