"""
=========================================================
LegalLens AI
Query Engine Models
=========================================================

Common result models used throughout the
Query Understanding pipeline.

Version: V4
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .query_types import QueryType


# =========================================================
# Intent Result
# =========================================================

@dataclass(slots=True)
class IntentResult:
    """
    Result returned by IntentClassifier.
    """

    query_type: QueryType

    confidence: float

    score: float

    normalized_query: str

    matched_keywords: list[str] = field(
        default_factory=list
    )


# =========================================================
# Token Correction
# =========================================================

@dataclass(slots=True)
class TokenCorrection:
    """
    Represents a single token correction.
    """

    original: str

    corrected: str

    confidence: float

    method: str


# =========================================================
# Spell Correction Result
# =========================================================

@dataclass(slots=True)
class SpellCorrectionResult:
    """
    Result returned by SpellCorrector.
    """

    original_query: str

    corrected_query: str

    confidence: float

    corrected_tokens: list[TokenCorrection] = field(
        default_factory=list
    )


# =========================================================
# Abbreviation Expansion
# =========================================================

@dataclass(slots=True)
class AbbreviationExpansion:
    """
    Represents one expanded abbreviation.
    """

    abbreviation: str

    expanded: str


# =========================================================
# Abbreviation Expansion Result
# =========================================================

@dataclass(slots=True)
class AbbreviationExpansionResult:
    """
    Result returned by AbbreviationExpander.
    """

    original_query: str

    expanded_query: str

    expanded_abbreviations: list[
        AbbreviationExpansion
    ] = field(
        default_factory=list
    )


# =========================================================
# Synonym Expansion
# =========================================================

@dataclass(slots=True)
class SynonymExpansion:
    """
    Represents one synonym expansion.
    """

    canonical: str

    matched_variant: str


# =========================================================
# Synonym Expansion Result
# =========================================================

@dataclass(slots=True)
class SynonymExpansionResult:
    """
    Result returned by SynonymExpander.
    """

    original_query: str

    expanded_query: str

    added_terms: list[
        SynonymExpansion
    ] = field(
        default_factory=list
    )


# =========================================================
# Fuzzy Match Result
# =========================================================

@dataclass(slots=True)
class MatchResult:
    """
    Result returned by FuzzyMatcher.
    """

    matched: bool

    original_text: str

    matched_text: str

    score: float

    method: str


@dataclass(slots=True)
class Entity:

    type: str

    value: str

    confidence: float


@dataclass(slots=True)
class EntityResult:

    original_query: str

    entities: list[Entity]