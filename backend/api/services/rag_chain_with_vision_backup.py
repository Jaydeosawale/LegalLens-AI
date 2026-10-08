from api.llm.llm_router import LLMRouter
from api.vision.vision_pipeline import VisionPipeline
from rag.citation.citation_service import CitationService
from rag.prompts.context_builder import ContextBuilder
from rag.prompts.prompt_builder import PromptBuilder
from rag.retrievers.context_compressor import ContextCompressor
from rag.retrievers.query_rewriter import QueryRewriter
from rag.retrievers.retrieval_pipeline import RetrievalPipeline


class RAGChain:
    """
    =========================================================
    Enterprise RAG Chain

    Responsibilities

    ✓ Query Rewrite
    ✓ Hybrid Retrieval
    ✓ Vision Pipeline
    ✓ Context Building
    ✓ Prompt Building
    ✓ LLM
    ✓ Citations

    Future

    ✓ Agent Planner
    ✓ Tool Calling
    ✓ Image Generation
    ✓ Web Search
    ✓ SQL Retrieval
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
    ):

        print("\n" + "=" * 80)
        print("NEW REQUEST")
        print("=" * 80)

        # --------------------------------------------------
        # Rewrite Query
        # --------------------------------------------------

        print("REWRITING QUERY")

        search_query = QueryRewriter.rewrite(
            question
        )

        print(
            "Original :",
            question,
        )

        print(
            "Search   :",
            search_query,
        )

        # --------------------------------------------------
        # Retrieve Documents
        # --------------------------------------------------

        print("\nRETRIEVING DOCUMENTS")

        documents = RetrievalPipeline.retrieve(
            question=search_query,
        )

        # --------------------------------------------------
        # Compress Context
        # --------------------------------------------------

        print("\nCOMPRESSING CONTEXT")

        documents = ContextCompressor.compress(
            question=question,
            documents=documents,
        )

        if not documents:

            print("NO DOCUMENTS FOUND")

            return {

                "answer":
                    "I couldn't find this information in the uploaded documents.",

                "documents": [],

                "citations": [],

                "images": [],

                "similar_images": [],

                "image_analysis": None,

            }

        # --------------------------------------------------
        # Vision
        # --------------------------------------------------

        print("\nRUNNING VISION PIPELINE")

        image_results = []

        similar_images = []

        image_analysis = None

        try:

            vision = VisionPipeline.process(

                question=question,

                search_query=search_query,

                uploaded_image=uploaded_image,

            )

            image_results = vision[
                "image_results"
            ]

            similar_images = vision[
                "similar_images"
            ]

            image_analysis = vision[
                "image_analysis"
            ]

        except Exception as e:

            print(
                "Vision Error:",
                e,
            )
                    # --------------------------------------------------
        # Build Context
        # --------------------------------------------------

        print("\nBUILDING CONTEXT")

        context = ContextBuilder.build(

            documents=documents,

            image_results=image_results,

            image_analysis=image_analysis,

        )

        print("=" * 80)
        print("Context Length :", len(context))
        print("=" * 80)

        # --------------------------------------------------
        # Conversation History
        # --------------------------------------------------

        print("\nBUILDING HISTORY")

        history = PromptBuilder.build_history(
            memory
        )

        # --------------------------------------------------
        # LLM
        # --------------------------------------------------

        print("\nLOADING LLM")

        llm = LLMRouter.get_llm()

        print("LLM READY")

        chain = PromptBuilder.build_chain(
            llm
        )

        # --------------------------------------------------
        # Generate Answer
        # --------------------------------------------------

        print("\n" + "=" * 80)
        print("GENERATING RESPONSE")
        print("=" * 80)

        answer = ""

        for chunk in chain.stream(

            {

                "history": history,

                "context": context,

                "question": question,

            }

        ):

            answer += chunk

        answer = answer.strip()

        print("=" * 80)
        print("LLM RESPONSE COMPLETE")
        print("=" * 80)

        print(
            "Answer Length :",
            len(answer),
        )

        print("=" * 80)
                # --------------------------------------------------
        # Debug Text → Image Results
        # --------------------------------------------------

        print("\n" + "=" * 80)
        print("TEXT → IMAGE RESULTS")
        print("=" * 80)

        print(
            "Images Found :",
            len(image_results),
        )

        for index, image in enumerate(
            image_results,
            start=1,
        ):

            print("\n" + "-" * 80)

            print(
                f"IMAGE {index}"
            )

            print(
                "PDF :",
                image.get(
                    "pdf_name",
                    "",
                ),
            )

            print(
                "Page :",
                image.get(
                    "page",
                    "",
                ),
            )

            print(
                "Caption :",
                image.get(
                    "caption",
                    "",
                ),
            )

            print(
                "Score :",
                image.get(
                    "score",
                    0,
                ),
            )

            print(
                "Path :",
                image.get(
                    "image_path",
                    "",
                ),
            )

        # --------------------------------------------------
        # Debug Image → Image
        # --------------------------------------------------

        if similar_images:

            print("\n" + "=" * 80)
            print("IMAGE → IMAGE RESULTS")
            print("=" * 80)

            for index, image in enumerate(
                similar_images,
                start=1,
            ):

                print("\n" + "-" * 80)

                print(
                    f"SIMILAR IMAGE {index}"
                )

                print(
                    "PDF :",
                    image.get(
                        "pdf_name",
                        "",
                    ),
                )

                print(
                    "Page :",
                    image.get(
                        "page",
                        "",
                    ),
                )

                print(
                    "Score :",
                    image.get(
                        "score",
                        0,
                    ),
                )

                print(
                    "Path :",
                    image.get(
                        "image_path",
                        "",
                    ),
                )

        # --------------------------------------------------
        # OCR Result
        # --------------------------------------------------

        if image_analysis:

            print("\n" + "=" * 80)
            print("OCR RESULT")
            print("=" * 80)

            print(
                image_analysis[:500]
            )

            print("=" * 80)

        # --------------------------------------------------
        # Build Citations
        # --------------------------------------------------

        print("\nBUILDING CITATIONS")

        citations = CitationService.build(
            documents
        )

        print(
            "Citations :",
            len(citations),
        )

        # --------------------------------------------------
        # Build Response
        # --------------------------------------------------

        response = {

            "answer": answer,

            "documents": documents,

            "citations": citations,

            "images": image_results,

            "similar_images": similar_images,

            "image_analysis": image_analysis,

        }

        # --------------------------------------------------
        # Request Summary
        # --------------------------------------------------

        print("\n" + "=" * 80)
        print("REQUEST COMPLETED")
        print("=" * 80)

        print(
            "Documents :",
            len(documents),
        )

        print(
            "Images :",
            len(image_results),
        )

        print(
            "Similar Images :",
            len(similar_images),
        )

        print(
            "Has OCR :",
            image_analysis is not None,
        )

        print(
            "Citations :",
            len(citations),
        )

        print("=" * 80)

        return response
            # =====================================================
    # Rewrite Query
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

        documents = RetrievalPipeline.retrieve(
            question=search_query,
        )

        return documents

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
    # Vision
    # =====================================================

    @staticmethod
    def process_vision(
        question,
        search_query,
        uploaded_image=None,
    ):

        try:

            return VisionPipeline.process(

                question=question,

                search_query=search_query,

                uploaded_image=uploaded_image,

            )

        except Exception as e:

            print("=" * 80)
            print("VISION PIPELINE FAILED")
            print(e)
            print("=" * 80)

            return {

                "image_results": [],

                "similar_images": [],

                "image_analysis": None,

            }

    # =====================================================
    # Build Context
    # =====================================================

    @staticmethod
    def build_context(
        documents,
        image_results,
        image_analysis,
    ):

        return ContextBuilder.build(

            documents=documents,

            image_results=image_results,

            image_analysis=image_analysis,

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
    # Build Response
    # =====================================================

    @staticmethod
    def build_response(

        answer,

        documents,

        citations,

        image_results,

        similar_images,

        image_analysis,

    ):

        return {

            "answer": answer,

            "documents": documents,

            "citations": citations,

            "images": image_results,

            "similar_images": similar_images,

            "image_analysis": image_analysis,

        }

    # =====================================================
    # Future Agent Planner
    # =====================================================

    @staticmethod
    def plan_tools(
        question,
    ):

        """
        Future

        Decide whether to use:

        • RAG
        • Vision
        • OCR
        • Image Generation
        • SQL
        • Web Search
        • Calculator

        """

        return {

            "use_rag": True,

            "use_vision": True,

            "use_generation": False,

            "use_web": False,

            "use_sql": False,

        }