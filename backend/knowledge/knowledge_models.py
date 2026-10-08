"""
=========================================================
LegalLens AI
Knowledge Models
=========================================================

Data models used by the Knowledge Layer.

These models represent the structure of the
LegalLens AI Knowledge Base.

Version: V1
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


# =========================================================
# Metadata
# =========================================================

@dataclass(slots=True)
class Metadata:
    """
    Knowledge base metadata.
    """

    name: str

    version: str

    description: str

    country: str

    default_language: str

    supported_languages: List[str]

    created_by: str

    created_at: str

    last_updated: str


# =========================================================
# Supported Models
# =========================================================

@dataclass(slots=True)
class SupportedModels:
    """
    Supported AI models.
    """

    ocr: List[str]

    vision: List[str]

    embeddings: List[str]

    rerankers: List[str]

    llms: List[str]


# =========================================================
# Entity Collections
# =========================================================

@dataclass(slots=True)
class Entities:
    """
    Structured entities.

    Used later by the Entity Extractor.
    """

    judges: List[str] = field(default_factory=list)

    states: List[str] = field(default_factory=list)

    cities: List[str] = field(default_factory=list)

    high_courts: List[str] = field(default_factory=list)

    ministries: List[str] = field(default_factory=list)

    government_departments: List[str] = field(default_factory=list)

    constitutional_articles: List[str] = field(default_factory=list)

    important_cases: List[str] = field(default_factory=list)


# =========================================================
# Knowledge Base
# =========================================================

@dataclass(slots=True)
class KnowledgeBase:
    """
    Complete LegalLens knowledge base.

    Loaded once at application startup.
    """

    metadata: Metadata

    models: SupportedModels

    abbreviations: Dict[str, str]

    synonyms: Dict[str, List[str]]

    legal_terms: List[str]

    courts: List[str]

    acts: List[str]

    legal_roles: List[str]

    latin_terms: List[str]

    vision_terms: List[str]

    ocr_terms: List[str]

    ai_terms: List[str]

    document_types: List[str]

    image_categories: List[str]

    stopwords: List[str]

    intent_keywords: Dict

    query_patterns: Dict

    aliases: Dict

    entities: Entities

    intent_keywords: dict[str, list[str]]

    rewrite_rules: dict

    routing_rules: dict

    canonical_terms: dict[str, str]