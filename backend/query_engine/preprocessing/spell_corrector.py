"""
=========================================================
LegalLens AI
Spell Corrector
=========================================================

Corrects spelling mistakes in user queries
using the centralized Knowledge Layer.

Features
--------
- Knowledge Layer vocabulary
- Token-level correction
- Confidence score
- RapidFuzz matching
- Cached vocabulary
- Cached token correction
- Preserves numbers
- Preserves punctuation
- Returns SpellCorrectionResult

Version: V3
"""

from __future__ import annotations

import re
from functools import lru_cache

from rapidfuzz import fuzz
from rapidfuzz import process

from knowledge import get_knowledge


from query_engine.classification.model import (
    SpellCorrectionResult,
    TokenCorrection,
)

class SpellCorrector:
    """
    Enterprise Legal Spell Corrector.
    """

    THRESHOLD = 85

    # =====================================================
    # Vocabulary
    # =====================================================

    @classmethod
    @lru_cache(maxsize=1)
    def vocabulary(
        cls,
    ) -> tuple[str, ...]:
        """
        Build vocabulary from the Knowledge Layer.
        """

        knowledge = get_knowledge()

        words: set[str] = set()

        # ---------------------------------------------
        # Abbreviations
        # ---------------------------------------------

        words.update(

            key.lower()

            for key in knowledge.abbreviations.keys()

        )

        words.update(

            value.lower()

            for value in knowledge.abbreviations.values()

        )

        # ---------------------------------------------
        # Synonyms
        # ---------------------------------------------

        for canonical, variants in knowledge.synonyms.items():

            words.add(
                canonical.lower()
            )

            words.update(

                variant.lower()

                for variant in variants

            )

        # ---------------------------------------------
        # Collections
        # ---------------------------------------------

        collections = [

            knowledge.legal_terms,

            knowledge.courts,

            knowledge.acts,

            knowledge.legal_roles,

            knowledge.latin_terms,

            knowledge.vision_terms,

            knowledge.ocr_terms,

            knowledge.ai_terms,

            knowledge.document_types,

            knowledge.image_categories,

        ]

        for collection in collections:

            for item in collection:

                words.add(
                    item.lower()
                )

        # ---------------------------------------------
        # Split multi-word phrases
        # ---------------------------------------------

        expanded = set()

        for phrase in words:

            expanded.add(
                phrase
            )

            expanded.update(
                phrase.split()
            )

        return tuple(
            sorted(expanded)
        )

    # =====================================================
    # Token Correction
    # =====================================================

    @classmethod
    @lru_cache(maxsize=4096)
    def correct_token(
        cls,
        token: str,
    ) -> tuple[str, float]:
        """
        Correct a single token.

        Returns
        -------
        corrected_token
        confidence
        """

        if not token:

            return token, 1.0

        if token.isdigit():

            return token, 1.0

        vocabulary = cls.vocabulary()

        if token in vocabulary:

            return token, 1.0

        result = process.extractOne(

            token,

            vocabulary,

            scorer=fuzz.ratio,

        )

        if result is None:

            return token, 0.0

        match, score, _ = result

        confidence = round(
            score / 100,
            2,
        )

        if score >= cls.THRESHOLD:

            return match, confidence

        return token, confidence

    # =====================================================
    # Query Correction
    # =====================================================

    @classmethod
    def correct(
        cls,
        query: str,
    ) -> SpellCorrectionResult:
        """
        Correct an entire query.

        Returns
        -------
        SpellCorrectionResult
        """

        if not query:

            return SpellCorrectionResult(

                original_query="",

                corrected_query="",

                confidence=0.0,

                corrected_tokens=[],

            )

        tokens = re.findall(

            r"\w+|[^\w\s]",

            query,

        )

        corrected_tokens = []

        corrected_query_tokens = []

        confidences = []

        for token in tokens:

            # Preserve punctuation

            if re.fullmatch(

                r"[^\w\s]",

                token,

            ):

                corrected_query_tokens.append(
                    token
                )

                continue

            corrected_token, confidence = (

                cls.correct_token(

                    token.lower()

                )

            )

            corrected_query_tokens.append(

                corrected_token

            )

            confidences.append(

                confidence

            )

            if corrected_token != token.lower():
                correction_method = (
                 "exact"
                if corrected_token == token.lower()
                else "fuzzy"
)

                corrected_tokens.append(

    TokenCorrection(

        original=token,

        corrected=corrected_token,

        confidence=confidence,
        method=correction_method,

    )

)

        corrected_query = " ".join(

            corrected_query_tokens

        )

        corrected_query = re.sub(

            r"\s+([.,!?;:])",

            r"\1",

            corrected_query,

        )

        overall_confidence = (

            sum(confidences) / len(confidences)

            if confidences

            else 1.0

        )

        return SpellCorrectionResult(

            original_query=query,

            corrected_query=corrected_query,

            confidence=round(

                overall_confidence,

                2,

            ),

            corrected_tokens=corrected_tokens,

        )