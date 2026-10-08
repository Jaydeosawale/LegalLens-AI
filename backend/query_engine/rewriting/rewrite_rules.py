"""
=========================================================
LegalLens AI
Rewrite Rules
=========================================================
"""

from __future__ import annotations

from query_engine.classification.query_types import QueryType


# =========================================================
# Remove filler words
# =========================================================

REMOVE_WORDS = {

    "what",

    "what is",

    "tell me",

    "please",

    "kindly",

    "describe",

    "explain",

    "give",

    "show me",

    "can you",

}


# =========================================================
# Intent-based additions
# =========================================================

INTENT_APPEND = {

    QueryType.IMAGE_SEARCH: [

        "image",

        "photo",

    ],

    QueryType.OCR: [

        "extract text",

    ],

    QueryType.LEGAL_SEARCH: [

        "constitution of india",

    ],

}