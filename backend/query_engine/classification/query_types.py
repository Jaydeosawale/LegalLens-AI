"""
=========================================================
LegalLens AI
Query Types
=========================================================
"""

from enum import Enum


class QueryType(str, Enum):

    GREETING = "greeting"

    TEXT = "text"

    LEGAL_SEARCH = "legal_search"

    OCR = "ocr"

    IMAGE = "image"

    IMAGE_SEARCH = "image_search"

    VISUAL_QA = "visual_qa"

    SUMMARIZATION = "summarization"

    CITATION = "citation"

    COMPARISON = "comparison"

    TIMELINE = "timeline"

    MULTIMODAL = "multimodal"

    UNKNOWN = "unknown"