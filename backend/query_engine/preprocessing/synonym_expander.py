"""
=========================================================
LegalLens AI
Synonym Expander
=========================================================

Expands canonical synonyms using the
Knowledge Layer.

Purpose
-------
- Query Expansion
- Intent Classification
- Entity Extraction
- Query Rewriting
- OCR
- Image Understanding

Version: V3
"""

from __future__ import annotations

from knowledge import get_synonyms


class SynonymExpander:
    """
    Expands query using canonical synonyms.

    Example
    -------
    photo

    →

    photo image

    judgment

    →

    judgment judgement decision ruling
    """

    def __init__(self) -> None:

        self.synonyms = get_synonyms()

    # =====================================================
    # Expand Query
    # =====================================================

    def expand(
        self,
        query: str,
    ) -> str:
        """
        Expand known synonyms.

        Parameters
        ----------
        query : str

        Returns
        -------
        str
        """

        if not query:

            return ""

        tokens = query.split()

        expanded = set(tokens)

        lower_query = query.lower()

        for canonical, variants in self.synonyms.items():

            # Canonical already present

            if canonical.lower() in lower_query:

                expanded.add(canonical)

                continue

            # Variant present

            for variant in variants:

                if variant.lower() in lower_query:

                    expanded.add(canonical)

                    break

        return " ".join(
            sorted(expanded)
        )