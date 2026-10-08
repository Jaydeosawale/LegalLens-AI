from api.llm.llm_router import LLMRouter

from rag.citation.citation_service import CitationService
from rag.prompts.context_builder import ContextBuilder
from rag.prompts.prompt_builder import PromptBuilder

from rag.retrievers.context_compressor import ContextCompressor
from rag.retrievers.query_rewriter import QueryRewriter
from rag.retrievers.retrieval_pipeline import RetrievalPipeline


class RAGChain:
    """
    =========================================================
    Legal Lens AI - Text RAG Chain
    =========================================================

    Active Pipeline:

    Question
        ↓
    Query Rewrite
        ↓
    Document Retrieval
        ↓
    Context Compression
        ↓
    Context Building
        ↓
    LLM
        ↓
    Answer + Citations

    Future:

    • Image RAG
    • OCR
    • Vision Search
    • Image Similarity
    • Web Search
    • Agent Tools
    =========================================================
    """

    # =====================================================
    # Main Entry
    # =====================================================

    @classmethod
    def ask(
        cls,
        question,
        memory=None,
        uploaded_image=None,
        user_id=None,
        document_ids=None,
        preferences=None,
    ):

        print("\n" + "=" * 80)
        print("NEW LEGAL LENS RAG REQUEST")
        print("=" * 80)

        # -------------------------------------------------
        # Uploaded images are temporarily disabled
        # -------------------------------------------------

        if uploaded_image is not None:

            print(
                "Image input received but Image RAG "
                "is currently disabled."
            )

        # -------------------------------------------------
        # Query Rewrite
        # -------------------------------------------------

        print("\nREWRITING QUERY")

        search_query = QueryRewriter.rewrite(
            question
        )

        # -------------------------------------------------
        # Retrieve Documents
        # -------------------------------------------------

        print("\nRETRIEVING DOCUMENTS")

        documents = RetrievalPipeline.retrieve(
            question=search_query,
            user_id=user_id,
            document_ids=document_ids,
        )

        print(
            "Documents Retrieved:",
            len(documents),
        )

        # -------------------------------------------------
        # Context Compression
        # -------------------------------------------------

        print("\nCOMPRESSING CONTEXT")

        documents = ContextCompressor.compress(
            question=question,
            documents=documents,
        )

        print(
            "Documents After Compression:",
            len(documents),
        )

        # -------------------------------------------------
        # No Documents
        # -------------------------------------------------

        if not documents:

            print("\nNO DOCUMENTS FOUND")

            return {

                "answer": (
                    "I couldn't find relevant information "
                    "in the available legal documents."
                ),

                "documents": [],

                "citations": [],

                # Kept for frontend API compatibility
                "images": [],
                "similar_images": [],
                "image_analysis": None,

            }

        # -------------------------------------------------
        # Build Text Context
        # -------------------------------------------------

        print("\nBUILDING CONTEXT")

        context = ContextBuilder.build(

            documents=documents,

            # Image RAG temporarily disabled
            image_results=[],

            image_analysis=None,

        )

        print("=" * 80)

        print(
            "Context Length:",
            len(context),
        )

        print("=" * 80)

        # -------------------------------------------------
        # Conversation History
        # -------------------------------------------------

        print("\nBUILDING HISTORY")

        history = PromptBuilder.build_history(
            memory or []
        )

        # -------------------------------------------------
        # Load LLM
        # -------------------------------------------------

        print("\nLOADING LLM")

        llm = LLMRouter.get_llm()

        print("LLM READY")

        chain = PromptBuilder.build_chain(
            llm
        )

        # -------------------------------------------------
        # Generate Answer
        # -------------------------------------------------

        print("\n" + "=" * 80)
        print("GENERATING RESPONSE")
        print("=" * 80)

        answer = cls.generate_answer(

            chain=chain,

            history=history,

            context=context,

            question=question + (f"\nRespond in {preferences['language']} with a {preferences['response_style'].lower()} explanation and source citations." if preferences else ""),

        )

        print("=" * 80)
        print("LLM RESPONSE COMPLETE")
        print("Answer Length:", len(answer))
        print("=" * 80)

        # -------------------------------------------------
        # Citations
        # -------------------------------------------------

        print("\nBUILDING CITATIONS")

        citations = CitationService.build(
            documents
        )

        print(
            "Citations:",
            len(citations),
        )

        # -------------------------------------------------
        # Response
        # -------------------------------------------------

        response = {

            "answer": answer,

            "documents": documents,

            "citations": citations,

            # Kept for frontend compatibility
            "images": [],
            "similar_images": [],
            "image_analysis": None,

        }

        print("\n" + "=" * 80)
        print("REQUEST COMPLETED")
        print("=" * 80)

        print(
            "Documents:",
            len(documents),
        )

        print(
            "Citations:",
            len(citations),
        )

        print("=" * 80)

        return response

    # =====================================================
    # Query Rewrite
    # =====================================================

    @staticmethod
    def rewrite_query(
        question,
    ):

        return QueryRewriter.rewrite(
            question
        )

    # =====================================================
    # Retrieve Documents
    # =====================================================

    @staticmethod
    def retrieve_documents(
        search_query,
    ):

        return RetrievalPipeline.retrieve(
            question=search_query,
        )

    # =====================================================
    # Compress Context
    # =====================================================

    @staticmethod
    def compress_documents(
        question,
        documents,
    ):

        return ContextCompressor.compress(
            question=question,
            documents=documents,
        )

    # =====================================================
    # Build Text Context
    # =====================================================

    @staticmethod
    def build_context(
        documents,
    ):

        return ContextBuilder.build(

            documents=documents,

            image_results=[],

            image_analysis=None,

        )

    # =====================================================
    # Generate Answer
    # =====================================================

    @staticmethod
    def generate_answer(
        chain,
        history,
        context,
        question,
    ):

        answer = ""

        for chunk in chain.stream(

            {

                "history": history,

                "context": context,

                "question": question,

            }

        ):

            answer += chunk

        return answer.strip()

    # =====================================================
    # Future Agent Planner
    # =====================================================

    @staticmethod
    def plan_tools(
        question,
    ):

        """
        Future tool planning.
        """

        return {

            "use_rag": True,

            "use_vision": False,

            "use_generation": False,

            "use_web": False,

            "use_sql": False,

        }
