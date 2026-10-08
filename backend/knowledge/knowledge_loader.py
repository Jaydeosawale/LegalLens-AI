"""
=========================================================
LegalLens AI
Knowledge Loader
=========================================================

Loads and validates the LegalLens AI
Knowledge Base.

Features
--------
- Singleton-friendly
- Cached loading
- Strong validation
- Typed models
- Helper methods

Version: V1
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .knowledge_models import (
    Entities,
    KnowledgeBase,
    Metadata,
    SupportedModels,
)


# =========================================================
# Exceptions
# =========================================================

class KnowledgeValidationError(Exception):
    """
    Raised when the knowledge base
    is invalid.
    """


# =========================================================
# Knowledge Loader
# =========================================================

class KnowledgeLoader:
    """
    Loads LegalLens AI knowledge base.
    """

    REQUIRED_KEYS = {

        "metadata",

        "models",

        "abbreviations",

        "synonyms",

        "legal_terms",

        "courts",

        "acts",

        "legal_roles",

        "latin_terms",

        "vision_terms",

        "ocr_terms",

        "ai_terms",

        "document_types",

        "image_categories",

        "stopwords",

        "intent_keywords",

        "query_patterns",

        "aliases",

        "entities",

    }

    # -----------------------------------------------------

    def __init__(
        self,
        path: str | Path,
    ) -> None:

        self.path = Path(path)

        self._knowledge = self._load()

    # =====================================================
    # Load JSON
    # =====================================================

    def _load(
        self,
    ) -> KnowledgeBase:

        if not self.path.exists():

            raise FileNotFoundError(

                f"Knowledge file not found: {self.path}"

            )

        with open(

            self.path,

            encoding="utf-8",

        ) as f:

            data = json.load(f)

        self._validate(data)

        return self._build(data)

    # =====================================================
    # Validation
    # =====================================================

    def _validate(
        self,
        data: dict[str, Any],
    ) -> None:

        missing = self.REQUIRED_KEYS - set(data.keys())

        if missing:

            raise KnowledgeValidationError(

                "Missing keys: "

                + ", ".join(sorted(missing))

            )

    # =====================================================
    # Build Models
    # =====================================================

    def _build(
        self,
        data: dict[str, Any],
    ) -> KnowledgeBase:

        metadata = Metadata(

            **data["metadata"]

        )

        models = SupportedModels(

            **data["models"]

        )

        entities = Entities(

            **data["entities"]

        )

        return KnowledgeBase(

            metadata=metadata,

            models=models,

            abbreviations=data["abbreviations"],

            synonyms=data["synonyms"],

            legal_terms=data["legal_terms"],

            courts=data["courts"],

            acts=data["acts"],

            legal_roles=data["legal_roles"],

            latin_terms=data["latin_terms"],

            vision_terms=data["vision_terms"],

            ocr_terms=data["ocr_terms"],

            ai_terms=data["ai_terms"],

            document_types=data["document_types"],

            image_categories=data["image_categories"],

            stopwords=data["stopwords"],

            intent_keywords=data["intent_keywords"],

            query_patterns=data["query_patterns"],

            aliases=data["aliases"],

            entities=entities,

        )

    # =====================================================
    # Public API
    # =====================================================

    @property
    def knowledge(
        self,
    ) -> KnowledgeBase:

        return self._knowledge

    # =====================================================
    # Convenience Methods
    # =====================================================

    def get_metadata(self):

        return self._knowledge.metadata

    def get_models(self):

        return self._knowledge.models

    def get_abbreviations(self):

        return self._knowledge.abbreviations

    def get_synonyms(self):

        return self._knowledge.synonyms

    def get_legal_terms(self):

        return self._knowledge.legal_terms

    def get_courts(self):

        return self._knowledge.courts

    def get_acts(self):

        return self._knowledge.acts

    def get_roles(self):

        return self._knowledge.legal_roles

    def get_latin_terms(self):

        return self._knowledge.latin_terms

    def get_vision_terms(self):

        return self._knowledge.vision_terms

    def get_ocr_terms(self):

        return self._knowledge.ocr_terms

    def get_ai_terms(self):

        return self._knowledge.ai_terms

    def get_document_types(self):

        return self._knowledge.document_types

    def get_image_categories(self):

        return self._knowledge.image_categories

    def get_stopwords(self):

        return self._knowledge.stopwords

    def get_entities(self):

        return self._knowledge.entities

    def get_intent_keywords(self):
        return self.knowledge.intent_keywords

    def get_rewrite_rules(self):

        return self.knowledge.rewrite_rules


    def get_routing_rules(self):

       return self.knowledge.routing_rules

    def get_canonical_terms(self):
     return self.knowledge.canonical_terms