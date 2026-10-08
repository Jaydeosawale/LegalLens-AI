"""
=========================================================
LegalLens AI
Entity Extractor
=========================================================

Extracts structured entities from a
preprocessed query.

Pipeline
--------
Normalized Query
        ↓
Exact Matching
        ↓
Fuzzy Matching
        ↓
Knowledge Layer
        ↓
EntityResult

Features
--------
✓ Exact Matching
✓ Fuzzy Matching
✓ Multi-word Entity Detection
✓ Confidence Scoring
✓ Duplicate Removal
✓ Knowledge Layer Integration

Version: V1
"""

from __future__ import annotations

from typing import Iterable

from knowledge import get_knowledge

from ..preprocessing.fuzzy_matcher import FuzzyMatcher

from ..classification.models import (
    Entity,
    EntityResult,
)


class EntityExtractor:
    """
    Extract structured entities from a query.
    """

    EXACT_CONFIDENCE = 1.0

    FUZZY_CONFIDENCE = 0.85

    def __init__(self) -> None:
        """
        Load knowledge once.
        """

        knowledge = get_knowledge()

        self.courts = knowledge.courts

        self.acts = knowledge.acts

        self.legal_terms = knowledge.legal_terms

        self.roles = knowledge.legal_roles

        self.latin_terms = knowledge.latin_terms

        self.vision_terms = knowledge.vision_terms

        self.ocr_terms = knowledge.ocr_terms

        self.ai_terms = knowledge.ai_terms

        self.document_types = knowledge.document_types

        self.image_categories = knowledge.image_categories

        self.entities = knowledge.entities

    # =====================================================
    # Exact Matching
    # =====================================================

    def _exact_match(
        self,
        query: str,
        values: Iterable[str],
        entity_type: str,
    ) -> list[Entity]:

        found = []

        query_lower = query.lower()

        tokens = set(query_lower.split())

        for value in values:

            value_lower = value.lower()

            if " " in value_lower:

                matched = value_lower in query_lower

            else:

                matched = value_lower in tokens

            if matched:

                found.append(

                    Entity(

                        entity_type=entity_type,

                        value=value,

                        confidence=self.EXACT_CONFIDENCE,

                    )

                )

        return found

    # =====================================================
    # Fuzzy Matching
    # =====================================================

    def _fuzzy_match(
        self,
        query: str,
        values: Iterable[str],
        entity_type: str,
    ) -> list[Entity]:

        found = []

        tokens = query.lower().split()

        for value in values:

            value_lower = value.lower()

            matched = False

            confidence = 0.0

            if " " in value_lower:

                similarity = FuzzyMatcher.weighted_score(

                    query.lower(),

                    value_lower,

                )

                if similarity >= FuzzyMatcher.THRESHOLD:

                    matched = True

                    confidence = similarity / 100

            else:

                for token in tokens:

                    similarity = FuzzyMatcher.weighted_score(

                        token,

                        value_lower,

                    )

                    if similarity >= FuzzyMatcher.THRESHOLD:

                        matched = True

                        confidence = similarity / 100

                        break

            if matched:

                found.append(

                    Entity(

                        entity_type=entity_type,

                        value=value,

                        confidence=round(

                            confidence,

                            2,

                        ),

                    )

                )

        return found
            # =====================================================
    # Courts
    # =====================================================

    def _extract_courts(
        self,
        query: str,
    ) -> list[Entity]:

        entities = self._exact_match(

            query,

            self.courts,

            "court",

        )

        if entities:

            return entities

        return self._fuzzy_match(

            query,

            self.courts,

            "court",

        )

    # =====================================================
    # Acts
    # =====================================================

    def _extract_acts(
        self,
        query: str,
    ) -> list[Entity]:

        entities = self._exact_match(

            query,

            self.acts,

            "act",

        )

        if entities:

            return entities

        return self._fuzzy_match(

            query,

            self.acts,

            "act",

        )

    # =====================================================
    # Legal Terms
    # =====================================================

    def _extract_legal_terms(
        self,
        query: str,
    ) -> list[Entity]:

        entities = self._exact_match(

            query,

            self.legal_terms,

            "legal_term",

        )

        if entities:

            return entities

        return self._fuzzy_match(

            query,

            self.legal_terms,

            "legal_term",

        )

    # =====================================================
    # Legal Roles
    # =====================================================

    def _extract_roles(
        self,
        query: str,
    ) -> list[Entity]:

        entities = self._exact_match(

            query,

            self.roles,

            "legal_role",

        )

        if entities:

            return entities

        return self._fuzzy_match(

            query,

            self.roles,

            "legal_role",

        )

    # =====================================================
    # Latin Terms
    # =====================================================

    def _extract_latin_terms(
        self,
        query: str,
    ) -> list[Entity]:

        entities = self._exact_match(

            query,

            self.latin_terms,

            "latin_term",

        )

        if entities:

            return entities

        return self._fuzzy_match(

            query,

            self.latin_terms,

            "latin_term",

        )

    # =====================================================
    # Vision Terms
    # =====================================================

    def _extract_vision_terms(
        self,
        query: str,
    ) -> list[Entity]:

        entities = self._exact_match(

            query,

            self.vision_terms,

            "vision",

        )

        if entities:

            return entities

        return self._fuzzy_match(

            query,

            self.vision_terms,

            "vision",

        )

    # =====================================================
    # OCR Terms
    # =====================================================

    def _extract_ocr_terms(
        self,
        query: str,
    ) -> list[Entity]:

        entities = self._exact_match(

            query,

            self.ocr_terms,

            "ocr",

        )

        if entities:

            return entities

        return self._fuzzy_match(

            query,

            self.ocr_terms,

            "ocr",

        )

    # =====================================================
    # AI Terms
    # =====================================================

    def _extract_ai_terms(
        self,
        query: str,
    ) -> list[Entity]:

        entities = self._exact_match(

            query,

            self.ai_terms,

            "ai",

        )

        if entities:

            return entities

        return self._fuzzy_match(

            query,

            self.ai_terms,

            "ai",

        )

    # =====================================================
    # Document Types
    # =====================================================

    def _extract_document_types(
        self,
        query: str,
    ) -> list[Entity]:

        entities = self._exact_match(

            query,

            self.document_types,

            "document",

        )

        if entities:

            return entities

        return self._fuzzy_match(

            query,

            self.document_types,

            "document",

        )

    # =====================================================
    # Image Categories
    # =====================================================

    def _extract_image_categories(
        self,
        query: str,
    ) -> list[Entity]:

        entities = self._exact_match(

            query,

            self.image_categories,

            "image_category",

        )

        if entities:

            return entities

        return self._fuzzy_match(

            query,

            self.image_categories,

            "image_category",

        )

    # =====================================================
    # Generic Knowledge Entities
    # =====================================================

    def _extract_generic_entities(
        self,
        query: str,
    ) -> list[Entity]:

        entities = self._exact_match(

            query,

            self.entities,

            "entity",

        )

        if entities:

            return entities

        return self._fuzzy_match(

            query,

            self.entities,

            "entity",

        )
            # =====================================================
    # Remove Duplicate Entities
    # =====================================================

    def _deduplicate(
        self,
        entities: list[Entity],
    ) -> list[Entity]:
        """
        Remove duplicate entities while keeping
        the highest confidence match.
        """

        unique: dict[tuple[str, str], Entity] = {}

        for entity in entities:

            key = (

                entity.entity_type.lower(),

                entity.value.lower(),

            )

            existing = unique.get(key)

            if (

                existing is None

                or entity.confidence > existing.confidence

            ):

                unique[key] = entity

        return sorted(

            unique.values(),

            key=lambda e: (

                -e.confidence,

                e.entity_type,

                e.value,

            ),

        )

    # =====================================================
    # Extract Entities
    # =====================================================

    def extract(
        self,
        query: str,
    ) -> EntityResult:
        """
        Extract structured entities from a query.
        """

        if not query:

            return EntityResult(

                original_query="",

                entities=[],

            )

        entities: list[Entity] = []

        # ---------------------------------------------
        # Knowledge Collections
        # ---------------------------------------------

        entities.extend(

            self._extract_courts(

                query

            )

        )

        entities.extend(

            self._extract_acts(

                query

            )

        )

        entities.extend(

            self._extract_legal_terms(

                query

            )

        )

        entities.extend(

            self._extract_roles(

                query

            )

        )

        entities.extend(

            self._extract_latin_terms(

                query

            )

        )

        entities.extend(

            self._extract_vision_terms(

                query

            )

        )

        entities.extend(

            self._extract_ocr_terms(

                query

            )

        )

        entities.extend(

            self._extract_ai_terms(

                query

            )

        )

        entities.extend(

            self._extract_document_types(

                query

            )

        )

        entities.extend(

            self._extract_image_categories(

                query

            )

        )

        entities.extend(

            self._extract_generic_entities(

                query

            )

        )

        # ---------------------------------------------
        # Numbers
        # ---------------------------------------------

        import re

        for number in re.findall(

            r"\b\d+\b",

            query,

        ):

            entities.append(

                Entity(

                    entity_type="number",

                    value=number,

                    confidence=1.0,

                )

            )

        # ---------------------------------------------
        # Years
        # ---------------------------------------------

        for year in re.findall(

            r"\b(18\d{2}|19\d{2}|20\d{2}|21\d{2})\b",

            query,

        ):

            entities.append(

                Entity(

                    entity_type="year",

                    value=year,

                    confidence=1.0,

                )

            )

        # ---------------------------------------------
        # Deduplicate
        # ---------------------------------------------

        entities = self._deduplicate(

            entities

        )

        # ---------------------------------------------
        # Return
        # ---------------------------------------------

        return EntityResult(

            original_query=query,

            entities=entities,

        )