"""
=========================================================
LegalLens AI
Score Filter
=========================================================
"""


class ScoreFilter:
    """
    Filters low quality retrieved documents.

    Future:
        • Dynamic thresholds
        • Per-document thresholds
        • Metadata-aware filtering
    """

    @staticmethod
    def filter(
        documents,
        minimum_score=0.0,
    ):

        if not documents:
            return []

        filtered = []

        for doc in documents:

            score = doc.metadata.get(
                "score",
                1.0,
            )

            if score >= minimum_score:
                filtered.append(doc)

        print("=" * 80)
        print("SCORE FILTER")
        print(
            f"Before : {len(documents)}"
        )
        print(
            f"After  : {len(filtered)}"
        )
        print("=" * 80)

        return filtered