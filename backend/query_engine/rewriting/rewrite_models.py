"""
=========================================================
LegalLens AI
Rewrite Models
=========================================================

Models used by the Rule Query Rewriter.

Version: V2
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field


# =========================================================
# Query Rewrite
# =========================================================

@dataclass(slots=True)
class QueryRewrite:
    """
    Represents a single rewrite operation.
    """

    # Original text
    original: str

    # Rewritten text
    rewritten: str

    # Why rewrite happened
    reason: str

    # Rewrite priority
    priority: int = 0

    # Rewrite confidence
    confidence: float = 1.0


# =========================================================
# Query Rewrite Result
# =========================================================

@dataclass(slots=True)
class QueryRewriteResult:
    """
    Final rewritten query returned by
    RuleQueryRewriter.
    """

    # Original query
    original_query: str

    # Final rewritten query
    rewritten_query: str

    # Rewrite history
    rewrites: list[QueryRewrite] = field(
        default_factory=list
    )

    # Number of rewrites performed
    rewrite_count: int = 0

    # Overall confidence
    overall_confidence: float = 1.0