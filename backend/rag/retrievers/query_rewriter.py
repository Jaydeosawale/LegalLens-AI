"""Normalize search phrasing without inventing terms or spending an AI call."""
import re
import unicodedata


class QueryRewriter:
    @staticmethod
    def rewrite(question: str) -> str:
        query = ' '.join(unicodedata.normalize('NFKC', question).casefold().split())
        query = query.rstrip('?.!').strip()
        # Keep qualifiers, dates, negation and section numbers intact.
        normalized = re.sub(
            r'^(?:please\s+)?(?:what\s+(?:is|are)\s+|define\s+|explain\s+|tell\s+me\s+about\s+)',
            '', query, count=1,
        ).strip()
        return normalized or query
