"""
=========================================================
LegalLens AI
Query Analyzer
=========================================================
"""


class QueryAnalyzer:
    """
    Analyzes the user's query to determine which retrieval
    strategy should be used.

    Detects

    • Query Type
    • Image Search
    • Summary Requests
    • Comparison Queries
    • Page Filters
    • Document Filters
    • Neighbor Retrieval
    • Multi Query Retrieval
    """

    IMAGE_KEYWORDS = {
        "image",
        "photo",
        "picture",
        "diagram",
        "figure",
        "logo",
        "seal",
        "stamp",
        "signature",
        "chart",
        "graph",
    }

    SUMMARY_KEYWORDS = {
        "summary",
        "summarize",
        "overview",
        "brief",
        "gist",
        "explain",
    }

    COMPARISON_KEYWORDS = {
        "compare",
        "difference",
        "differences",
        "similar",
        "similarity",
        "versus",
        "vs",
    }

    OCR_KEYWORDS = {
        "scan",
        "scanned",
        "ocr",
        "handwritten",
        "text in image",
    }

    @staticmethod
    def analyze(question: str):

        q = question.lower()

        words = set(q.split())

        # --------------------------------------------------
        # Intent Detection
        # --------------------------------------------------

        needs_images = any(
            word in q
            for word in QueryAnalyzer.IMAGE_KEYWORDS
        )

        needs_summary = any(
            word in q
            for word in QueryAnalyzer.SUMMARY_KEYWORDS
        )

        needs_comparison = any(
            word in q
            for word in QueryAnalyzer.COMPARISON_KEYWORDS
        )

        needs_ocr = any(
            word in q
            for word in QueryAnalyzer.OCR_KEYWORDS
        )

        needs_page_filter = (
            "page " in q
            or "page no" in q
            or "page number" in q
        )

        needs_document_filter = (
            ".pdf" in q
            or "document" in words
            or "file" in words
        )

        # --------------------------------------------------
        # Query Type
        # --------------------------------------------------

        if needs_images:
            query_type = "image"

        elif needs_comparison:
            query_type = "comparison"

        elif needs_summary:
            query_type = "summary"

        elif needs_ocr:
            query_type = "ocr"

        else:
            query_type = "legal"

        # --------------------------------------------------
        # Retrieval Strategy
        # --------------------------------------------------

        return {

            # ------------------------------
            # Classification
            # ------------------------------

            "query_type": query_type,

            # ------------------------------
            # Retrieval
            # ------------------------------

            "needs_multi_query": (
                needs_summary
                or needs_comparison
            ),

            "needs_neighbors": (
                not needs_images
            ),

            "needs_images": needs_images,

            "needs_summary": needs_summary,

            "needs_comparison": needs_comparison,

            "needs_ocr": needs_ocr,

            "needs_page_filter": needs_page_filter,

            "needs_document_filter": needs_document_filter,

            # ------------------------------
            # Future Expansion
            # ------------------------------

            "needs_metadata_filter": (
                needs_page_filter
                or needs_document_filter
            ),

            "top_k": (
                15
                if needs_summary
                else 8
            ),
        }