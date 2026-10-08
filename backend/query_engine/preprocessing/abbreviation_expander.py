"""
=========================================================
LegalLens AI
Abbreviation Expander
=========================================================

Expands legal abbreviations into their
canonical form using the centralized
Knowledge Layer.

Features
--------
- Knowledge Layer integration
- Case-insensitive expansion
- Tracks expanded abbreviations
- Returns AbbreviationExpansionResult

Version: V3
"""

from __future__ import annotations

import re

from knowledge import get_abbreviations

from ..models import AbbreviationExpansionResult


class AbbreviationExpander:
    """
    Expands legal abbreviations using the
    centralized Knowledge Layer.
    """

    def __init__(self) -> None:

        self.abbreviations = {

            key.lower(): value.lower()

            for key, value in get_abbreviations().items()

        }

    # =====================================================
    # Expand Query
    # =====================================================

    def expand(
        self,
        query: str,
    ) -> AbbreviationExpansionResult:
        """
        Expand abbreviations.

        Parameters
        ----------
        query : str

        Returns
        -------
        AbbreviationExpansionResult
        """

        if not query:

            return AbbreviationExpansionResult(

                original_query="",

                expanded_query="",

                expanded_abbreviations=[],

            )

        expanded_tokens = []

        expanded_abbreviations = []

        for token in query.split():

            cleaned = re.sub(

                r"[^\w.]",

                "",

                token.lower(),

            )

            expanded = self.abbreviations.get(

                cleaned,

                token,

            )

            expanded_tokens.append(

                expanded

            )

            if expanded.lower() != token.lower():

                expanded_abbreviations.append(

                    (

                        token,

                        expanded,

                    )

                )

        expanded_query = " ".join(

            expanded_tokens

        )

        return AbbreviationExpansionResult(

            original_query=query,

            expanded_query=expanded_query,

            expanded_abbreviations=expanded_abbreviations,

        )