"""
=========================================================
LegalLens AI
Fuzzy Matcher
=========================================================

Provides fuzzy string matching utilities
using RapidFuzz.

Features
--------
- Exact similarity score
- Partial similarity
- Token sort similarity
- Token set similarity
- Best match search
- Boolean match
- Returns MatchResult

Version: V2
"""

from __future__ import annotations

from rapidfuzz import fuzz
from rapidfuzz import process

from query_engine.classification.model import MatchResult


class FuzzyMatcher:
    """
    Enterprise fuzzy matcher.
    """

    THRESHOLD = 85

    # =====================================================
    # Ratio
    # =====================================================

    @staticmethod
    def ratio(
        text1: str,
        text2: str,
    ) -> float:
        """
        Standard similarity ratio.
        """

        return float(
            fuzz.ratio(
                text1,
                text2,
            )
        )

    # =====================================================
    # Partial Ratio
    # =====================================================

    @staticmethod
    def partial_ratio(
        text1: str,
        text2: str,
    ) -> float:
        """
        Partial similarity ratio.
        """

        return float(
            fuzz.partial_ratio(
                text1,
                text2,
            )
        )

    # =====================================================
    # Token Sort Ratio
    # =====================================================

    @staticmethod
    def token_sort_ratio(
        text1: str,
        text2: str,
    ) -> float:
        """
        Token order independent ratio.
        """

        return float(
            fuzz.token_sort_ratio(
                text1,
                text2,
            )
        )

    # =====================================================
    # Token Set Ratio
    # =====================================================

    @staticmethod
    def token_set_ratio(
        text1: str,
        text2: str,
    ) -> float:
        """
        Token set similarity.
        """

        return float(
            fuzz.token_set_ratio(
                text1,
                text2,
            )
        )

    # =====================================================
    # Weighted Score
    # =====================================================

    @classmethod
    def weighted_score(
        cls,
        text1: str,
        text2: str,
    ) -> float:
        """
        Average score from multiple
        RapidFuzz algorithms.
        """

        scores = [

            cls.ratio(
                text1,
                text2,
            ),

            cls.partial_ratio(
                text1,
                text2,
            ),

            cls.token_sort_ratio(
                text1,
                text2,
            ),

            cls.token_set_ratio(
                text1,
                text2,
            ),

        ]

        return round(

            sum(scores) / len(scores),

            2,

        )

    # =====================================================
    # Boolean Match
    # =====================================================

    @classmethod
    def is_match(
        cls,
        text1: str,
        text2: str,
    ) -> bool:
        """
        Check if two strings match.
        """

        return (

            cls.weighted_score(
                text1,
                text2,
            )

            >= cls.THRESHOLD

        )

    # =====================================================
    # Best Match
    # =====================================================

    @classmethod
    def best_match(
        cls,
        query: str,
        candidates: list[str],
    ) -> MatchResult:
        """
        Find best matching candidate.
        """

        if not candidates:

            return MatchResult(

                matched=False,

                matched_text="",

                score=0.0,

                method="none",

            )

        result = process.extractOne(

            query,

            candidates,

            scorer=fuzz.WRatio,

        )

        if result is None:

            return MatchResult(

                matched=False,

                matched_text="",

                score=0.0,

                method="WRatio",

            )

        match, score, _ = result

        return MatchResult(

            matched=score >= cls.THRESHOLD,

            matched_text=match,

            score=round(
                float(score),
                2,
            ),

            method="WRatio",

        )

    # =====================================================
    # Top Matches
    # =====================================================

    @classmethod
    def top_matches(
        cls,
        query: str,
        candidates: list[str],
        limit: int = 5,
    ) -> list[MatchResult]:
        """
        Return top matching candidates.
        """

        results = process.extract(

            query,

            candidates,

            scorer=fuzz.WRatio,

            limit=limit,

        )

        matches = []

        for match, score, _ in results:

            matches.append(

                MatchResult(

                    matched=score >= cls.THRESHOLD,

                    matched_text=match,

                    score=round(
                        float(score),
                        2,
                    ),

                    method="WRatio",

                )

            )

        return matches