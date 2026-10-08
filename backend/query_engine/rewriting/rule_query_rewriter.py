"""
=========================================================
LegalLens AI
Rule Query Rewriter
=========================================================

Performs deterministic query rewriting using
Knowledge Layer, Intent Classification and
Extracted Entities.

This module NEVER calls an LLM.

Pipeline
--------
Normalized Query
        ↓
Intent Result
        ↓
Entity Result
        ↓
Rewrite Rules
        ↓
QueryRewriteResult

Version: V1
"""

from __future__ import annotations

from knowledge import (
    get_rewrite_rules,
)

from query_engine.classification.model import (
    EntityResult,
    IntentResult,
)
import re

from knowledge import (
    get_rewrite_rules,
    get_canonical_terms,
)
from .rewrite_models import (
    QueryRewrite,
    QueryRewriteResult,
)


class RuleQueryRewriter:
    """
    Deterministic query rewriter.

    Uses:

    • Rewrite Rules
    • Intent
    • Extracted Entities

    Never calls an LLM.
    """

    def __init__(self) -> None:

        self.rules = get_rewrite_rules()
        self.canonical_terms = get_canonical_terms()
    # =====================================================
    # Remove Words
    # =====================================================

    def _remove_words(

        self,

        query: str,

        words: list[str],

        rewrites: list[QueryRewrite],

    ) -> str:

        rewritten = query

        for word in words:

            if word.lower() in rewritten.lower():

                rewritten = rewritten.replace(

                    word,

                    "",

                )

                rewrites.append(

                    QueryRewrite(

                        original=word,

                        rewritten="",

                        reason="remove filler",
                        priority=50,

                        confidence=1.0,

                    )

                )

        return " ".join(

            rewritten.split()

        )

    # =====================================================
    # Append Terms
    # =====================================================

    def _append_terms(

        self,

        query: str,

        terms: list[str],

        rewrites: list[QueryRewrite],

    ) -> str:

        rewritten = query

        lower = rewritten.lower()

        for term in terms:

            if term.lower() not in lower:

                rewritten += f" {term}"

                rewrites.append(

                    QueryRewrite(

                        original="",

                        rewritten=term,

                        reason="intent expansion",

                        priority=80,

                        confidence=1.0,

                    )

                )

        return rewritten.strip()

    # =====================================================
    # Entity Expansion
    # =====================================================

    def _expand_entities(

        self,

        query: str,

        entities: EntityResult,

        rewrites: list[QueryRewrite],

    ) -> str:

        rewritten = query

        lower = rewritten.lower()

        for entity in entities.entities:

            value = entity.value

            if value.lower() not in lower:

                rewritten += f" {value}"

                rewrites.append(

                    QueryRewrite(

                        original="",

                        rewritten=value,

                        reason=f"{entity.entity_type} expansion",
                        priority=90,

                        confidence=entity.confidence,

                    )

                )

        return rewritten.strip()
            # =====================================================
    # Canonicalize Query
    # =====================================================

    def _canonicalize(

        self,

        query: str,

        rewrites: list[QueryRewrite],

    ) -> str:
        """
        Normalize duplicate spaces and
        repeated words.
        """

        words = query.split()

        unique = []

        seen = set()

        for word in words:

            key = word.lower()

            if key in seen:

                rewrites.append(

                    QueryRewrite(

                        original=word,

                        rewritten="",

                        reason="duplicate removal",
                        priority=40,

                        confidence=1.0,

                    )

                )

                continue

            seen.add(key)

            unique.append(word)

        return " ".join(unique)

    # =====================================================
    # Intent Rewrite
    # =====================================================

    def _rewrite_by_intent(

        self,

        query: str,

        intent: IntentResult,

        rewrites: list[QueryRewrite],

    ) -> str:
        """
        Apply intent specific rewrite rules.
        """

        rule = self.rules.get(

            intent.query_type.name,

            {},

        )

        rewritten = query

        remove_words = rule.get(

            "remove",

            [],

        )

        append_words = rule.get(

            "append",

            [],

        )

        if remove_words:

            rewritten = self._remove_words(

                rewritten,

                remove_words,

                rewrites,

            )

        if append_words:

            rewritten = self._append_terms(

                rewritten,

                append_words,

                rewrites,

            )

        return rewritten

        # =====================================================
    # Legal Canonicalization
    # =====================================================

    def _legal_cleanup(

        self,

        query: str,

        rewrites: list[QueryRewrite],

    ) -> str:
        """
        Standardize legal terminology using
        canonical terms from the Knowledge Layer.
        """

        rewritten = query

        for old, new in self.canonical_terms.items():

            pattern = rf"\b{re.escape(old)}\b"

            if re.search(

                pattern,

                rewritten,

                flags=re.IGNORECASE,

            ):

                rewritten = re.sub(

                    pattern,

                    new,

                    rewritten,

                    flags=re.IGNORECASE,

                )

                rewrites.append(

                    QueryRewrite(

                        original=old,

                        rewritten=new,

                        reason="canonicalization",

                        priority=100,

                        confidence=1.0,

                    )

                )

        return rewritten

    # =====================================================
    # Final Cleanup
    # =====================================================

    def _cleanup(

        self,

        query: str,

    ) -> str:
        """
        Normalize whitespace.
        """

        return " ".join(

            query.split()

        )
            # =====================================================
    # Rewrite Query
    # =====================================================

    def rewrite(
        self,
        query: str,
        intent: IntentResult,
        entities: EntityResult,
    ) -> QueryRewriteResult:
        """
        Rewrite a query using deterministic rules.

        Parameters
        ----------
        query:
            Preprocessed query.

        intent:
            IntentClassifier output.

        entities:
            EntityExtractor output.

        Returns
        -------
        QueryRewriteResult
        """

        rewrites: list[QueryRewrite] = []

        rewritten = query.strip()

        # ---------------------------------------------
        # Intent Based Rules
        # ---------------------------------------------

        rewritten = self._rewrite_by_intent(

            rewritten,

            intent,

            rewrites,

        )

        # ---------------------------------------------
        # Entity Expansion
        # ---------------------------------------------

        rewritten = self._expand_entities(

            rewritten,

            entities,

            rewrites,

        )

        # ---------------------------------------------
        # Legal Canonicalization
        # ---------------------------------------------

        rewritten = self._legal_cleanup(

            rewritten,

            rewrites,

        )

        # ---------------------------------------------
        # Remove Duplicate Words
        # ---------------------------------------------

        rewritten = self._canonicalize(

            rewritten,

            rewrites,

        )

        # ---------------------------------------------
        # Final Cleanup
        # ---------------------------------------------

        rewritten = self._cleanup(

            rewritten,

        )

        # ---------------------------------------------
        # Build Result
        # ---------------------------------------------

        rewrites.sort(
    key=lambda rewrite: rewrite.priority,
    reverse=True,
)

        overall_confidence = (

         sum(
             rewrite.confidence
             for rewrite in rewrites
            ) / len(rewrites)

      if rewrites

       else 1.0

)

        return QueryRewriteResult(

        original_query=query,

        rewritten_query=rewritten,

       rewrites=rewrites,

       rewrite_count=len(rewrites),

       overall_confidence=round(
        overall_confidence,
        2,
     ),

)
