"""
=========================================================
LegalLens AI
Knowledge Cache
=========================================================

Provides a singleton-style cached instance of the
Knowledge Loader.

Features
--------
- Lazy loading
- Cached instance
- Thread-safe (Python import level)
- Central access point

Version: V1
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from .knowledge_loader import KnowledgeLoader


# =========================================================
# Default Knowledge Path
# =========================================================

DEFAULT_KNOWLEDGE_PATH = (
    Path(__file__).parent.parent
    / "resources"
    / "legal_knowledge.json"
)


# =========================================================
# Cached Loader
# =========================================================

@lru_cache(maxsize=1)
def get_loader() -> KnowledgeLoader:
    """
    Return cached KnowledgeLoader.

    Returns
    -------
    KnowledgeLoader
    """

    return KnowledgeLoader(
        DEFAULT_KNOWLEDGE_PATH
    )


# =========================================================
# Cached Knowledge
# =========================================================

def get_knowledge():
    """
    Return cached KnowledgeBase.

    Returns
    -------
    KnowledgeBase
    """

    return get_loader().knowledge


# =========================================================
# Helper Functions
# =========================================================

def get_metadata():

    return get_loader().get_metadata()


def get_models():

    return get_loader().get_models()


def get_abbreviations():

    return get_loader().get_abbreviations()


def get_synonyms():

    return get_loader().get_synonyms()


def get_legal_terms():

    return get_loader().get_legal_terms()


def get_courts():

    return get_loader().get_courts()


def get_acts():

    return get_loader().get_acts()


def get_roles():

    return get_loader().get_roles()


def get_latin_terms():

    return get_loader().get_latin_terms()


def get_vision_terms():

    return get_loader().get_vision_terms()


def get_ocr_terms():

    return get_loader().get_ocr_terms()


def get_ai_terms():

    return get_loader().get_ai_terms()


def get_document_types():

    return get_loader().get_document_types()


def get_image_categories():

    return get_loader().get_image_categories()


def get_stopwords():

    return get_loader().get_stopwords()


def get_entities():

    return get_loader().get_entities()

def get_intent_keywords():
    return get_loader().get_intent_keywords()

def get_rewrite_rules():

    return get_loader().get_rewrite_rules()


def get_routing_rules():

    return get_loader().get_routing_rules()

def get_canonical_terms():
    return get_loader().get_canonical_terms()