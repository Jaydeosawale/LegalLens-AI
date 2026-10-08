"""
=========================================================
Legal Lens AI
Startup Manager
=========================================================

Production startup configuration.

Current production architecture:

✓ Supabase PostgreSQL
✓ pgvector
✓ Sentence Transformer Embeddings
✓ Groq LLM

Future features:

- OCR
- Image RAG
- Vision Search
"""

from rag.embeddings.embeddings import EmbeddingModel
from api.llm.llm import LLMService


class StartupManager:
    """
    Initializes only the services required for
    the current Legal Lens production architecture.
    """

    initialized = False

    # ==================================================
    # Core AI Services
    # ==================================================

    embedding_model = None
    llm = None

    @classmethod
    def initialize(cls):

        if cls.initialized:

            print("=" * 80)
            print("SYSTEM ALREADY INITIALIZED")
            print("=" * 80)

            return

        print("=" * 80)
        print("INITIALIZING LEGAL LENS AI")
        print("=" * 80)

        # ==================================================
        # Embedding Model
        # ==================================================

        print("Loading embedding model...")

        cls.embedding_model = EmbeddingModel.get_model()

        print("✓ Embedding Model Ready")

        # ==================================================
        # Groq LLM
        # ==================================================

        print("Initializing LLM...")

        cls.llm = LLMService.get_llm()

        print("✓ LLM Ready")

        # ==================================================
        # Complete
        # ==================================================

        cls.initialized = True

        print("=" * 80)
        print("LEGAL LENS AI READY")
        print("=" * 80)

    # ==================================================
    # Statistics
    # ==================================================

    @classmethod
    def stats(cls):

        return {

            "initialized": cls.initialized,

            "embedding_loaded":
                cls.embedding_model is not None,

            "llm_loaded":
                cls.llm is not None,

            "vector_database":
                "Supabase PostgreSQL + pgvector",

        }
