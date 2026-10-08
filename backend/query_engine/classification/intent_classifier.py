"""
=========================================================
LegalLens AI
Intent Classifier
=========================================================

Determines user intent after the query has
passed through the preprocessing pipeline.

Pipeline
--------
UnicodeNormalizer
    ↓
TextNormalizer
    ↓
AbbreviationExpander
    ↓
SynonymExpander
    ↓
SpellCorrector
    ↓
IntentClassifier

Version: V4
"""

from __future__ import annotations

from knowledge import get_intent_keywords

from ..preprocessing.fuzzy_matcher import FuzzyMatcher

from .models import IntentResult
from .query_types import QueryType


class IntentClassifier:
    """
    Enterprise Rule-Based Intent Classifier.
    """

    EXACT_MATCH_WEIGHT = 3.0
    FUZZY_MATCH_WEIGHT = 1.5

    PRIORITY = [

        QueryType.OCR,

        QueryType.IMAGE_SEARCH,

        QueryType.IMAGE,

        QueryType.MULTIMODAL,

        QueryType.SUMMARIZATION,

        QueryType.LEGAL_SEARCH,

        QueryType.CITATION,

        QueryType.COMPARISON,

        QueryType.TIMELINE,

        QueryType.GREETING,

        QueryType.TEXT,

    ]

    def __init__(self) -> None:
        """
        Load intent keywords from the
        Knowledge Layer.
        """

        self.intent_rules = get_intent_keywords()

    # =====================================================
    # Intent Classification
    # =====================================================

    def classify(
        self,
        query: str,
    ) -> IntentResult:
        """
        Classify an already preprocessed query.
        """

        if not query:

            return IntentResult(

                query_type=QueryType.TEXT,

                confidence=0.0,

                score=0.0,

                normalized_query="",

                matched_keywords=[],

            )

        processed_query = query.lower()

        tokens = set(processed_query.split())

        scores: dict[QueryType, float] = {}

        matched_keywords: dict[
            QueryType,
            list[str],
        ] = {}

        # ---------------------------------------------
        # Calculate Scores
        # ---------------------------------------------

        for intent_name, keywords in self.intent_rules.items():

            query_type = QueryType[intent_name]

            score = 0.0

            matches = []

            for keyword in keywords:

                keyword = keyword.lower()

                # -------------------------------------
                # Exact Match
                # -------------------------------------

                if " " in keyword:

                    exact_match = keyword in processed_query

                else:

                    exact_match = keyword in tokens

                if exact_match:

                    score += self.EXACT_MATCH_WEIGHT

                    matches.append(keyword)

                    continue


                # -------------------------------------
                # Fuzzy Match
                # -------------------------------------

                matched = False

                # Multi-word keyword
                if " " in keyword:

                    similarity = FuzzyMatcher.weighted_score(

                    processed_query,

                    keyword,

    )

                if similarity >= FuzzyMatcher.THRESHOLD:

                 matched = True

                # Single-word keyword
                else:

                 for token in tokens:

                  similarity = FuzzyMatcher.weighted_score(

                  token,

                  keyword,

        )

                if similarity >= FuzzyMatcher.THRESHOLD:

                 matched = True

                break

                if matched:

                 score += self.FUZZY_MATCH_WEIGHT

                 matches.append(

                 f"{keyword} (fuzzy)"

    )


        # ---------------------------------------------
        # Resolve Best Intent
        # ---------------------------------------------

        best_type = QueryType.TEXT

        highest_score = 0.0

        best_matches = []

        for intent in self.PRIORITY:

            current_score = scores.get(

                intent,

                0.0,

            )

            if current_score > highest_score:

                highest_score = current_score

                best_type = intent

                best_matches = matched_keywords.get(

                    intent,

                    [],

                )

        # ---------------------------------------------
        # Confidence
        # ---------------------------------------------

        ordered_scores = sorted(

            scores.values(),

            reverse=True,

        )

        top = ordered_scores[0]

        second = (

            ordered_scores[1]

            if len(ordered_scores) > 1

            else 0.0

        )

        if top == 0:

            confidence = 0.0

        elif second == 0:

            confidence = 1.0

        else:

            confidence = round(

                top / (top + second),

                2,

            )

        # ---------------------------------------------
        # Return Result
        # ---------------------------------------------

        return IntentResult(

            query_type=best_type,

            confidence=confidence,

            score=round(

                highest_score,

                2,

            ),

            normalized_query=processed_query,

            matched_keywords=best_matches,

        )