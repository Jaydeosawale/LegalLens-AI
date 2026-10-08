"""
=========================================================
LegalLens AI
Knowledge Package
=========================================================

Centralized access to the Knowledge Layer.

Version: V2
"""

from __future__ import annotations

from .cache import (
    get_knowledge,
    get_abbreviations,
    get_synonyms,
    get_legal_terms,
    get_courts,
    get_acts,
    get_legal_roles,
    get_latin_terms,
    get_vision_terms,
    get_ocr_terms,
    get_ai_terms,
    get_document_types,
    get_image_categories,
    get_entities,
    get_intent_keywords,
    get_rewrite_rules,
    get_routing_rules,
    get_canonical_terms,
)

__all__ = [

    "get_knowledge",

    "get_abbreviations",

    "get_synonyms",

    "get_legal_terms",

    "get_courts",

    "get_acts",

    "get_legal_roles",

    "get_latin_terms",

    "get_vision_terms",

    "get_ocr_terms",

    "get_ai_terms",

    "get_document_types",

    "get_image_categories",

    "get_entities",

    "get_intent_keywords",

    "get_rewrite_rules",

    "get_routing_rules",

    "get_canonical_terms",

]