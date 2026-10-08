"""
=========================================================
LegalLens AI
Enterprise Query Selector
=========================================================
"""

from __future__ import annotations


class QuerySelector:
    """
    Enterprise Query Selector.

    Responsibilities

    ✓ Remove duplicate queries
    ✓ Limit number of queries
    ✓ Preserve order

    Future

    ✓ Intent classification
    ✓ Query ranking
    ✓ Metadata routing
    ✓ Adaptive query selection
    """

    @staticmethod
    def select(
        queries,
        max_queries=3,
    ):

        # ------------------------------------------
        # Normalize input
        # ------------------------------------------

        if isinstance(
            queries,
            str,
        ):

            queries = [
                queries
            ]

        if not queries:

            return []

        # ------------------------------------------
        # Remove duplicates
        # ------------------------------------------

        unique = []

        seen = set()

        for query in queries:

            query = query.strip()

            if not query:

                continue

            key = query.lower()

            if key in seen:

                continue

            seen.add(key)

            unique.append(query)

        # ------------------------------------------
        # Limit number of queries
        # ------------------------------------------

        selected = unique[:max_queries]

        print("=" * 80)
        print("QUERY SELECTOR")
        print("=" * 80)

        print(
            "Input Queries :",
            len(queries),
        )

        print(
            "Selected :",
            len(selected),
        )

        print("=" * 80)

        return selected