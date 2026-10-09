"""
=========================================================
LegalLens AI
Context Compressor
=========================================================

Uses an LLM to extract relevant sentences from retrieved
legal document chunks.

Behavior:

- Relevant extraction → keep compressed document
- No relevant content → remove document
- LLM/API failure → keep original document safely
"""

from copy import deepcopy
import os

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from api.llm.llm import LLMService


class ContextCompressor:

    PROMPT = ChatPromptTemplate.from_template(
        """
You are a legal document context extractor.

Given a user question and a legal document chunk,
extract only the exact sentences from the document
that are useful for answering the question.

Rules:

1. Do NOT summarize.
2. Do NOT rewrite.
3. Do NOT add information.
4. Preserve the original wording.
5. Preserve legally important context.
6. Return only sentences present in the document.
7. If no sentence is clearly relevant, return an empty string.

Question:
{question}

Document:
{document}
"""
    )

    @staticmethod
    def compress(
        question,
        documents,
    ):

        if not documents:
            return []

        if os.getenv("CONTEXT_COMPRESSION_ENABLED", "true").lower() != "true":
            return documents

        print()
        print("=" * 80)
        print("CONTEXT COMPRESSION")
        print("=" * 80)

        print(
            "Input Documents:",
            len(documents),
        )

        llm = LLMService.get_llm()

        chain = (
            ContextCompressor.PROMPT
            | llm
            | StrOutputParser()
        )

        compressed = []

        for index, doc in enumerate(
            documents,
            start=1,
        ):

            print()
            print(
                f"Compressing Document {index}..."
            )

            # =============================================
            # LLM FAILURE
            # Keep original document safely
            # =============================================

            try:

                result = chain.invoke(
                    {
                        "question": question,
                        "document": doc.page_content,
                    }
                )

                result = result.strip()

            except Exception as error:

                print(
                    "Compression failed."
                )

                print(
                    "Keeping original document."
                )

                print(
                    "Reason:",
                    error,
                )

                original_doc = deepcopy(doc)

                original_doc.metadata = {
                    **original_doc.metadata,
                    "context_compressed": False,
                    "compression_failed": True,
                }

                compressed.append(original_doc)

                continue

            # =============================================
            # NO RELEVANT CONTENT
            # LLM succeeded but found nothing useful
            # Remove document
            # =============================================

            if not result:

                print(
                    "No relevant content found."
                )

                print(
                    "Removing irrelevant document."
                )

                continue

            # =============================================
            # RELEVANT CONTENT FOUND
            # Keep compressed document
            # =============================================

            new_doc = deepcopy(doc)

            new_doc.page_content = result

            new_doc.metadata = {
                **new_doc.metadata,
                "context_compressed": True,
                "compression_failed": False,
                "original_length": len(
                    doc.page_content
                ),
                "compressed_length": len(
                    result
                ),
            }

            compressed.append(new_doc)

            print(
                "Compression successful."
            )

            print(
                "Original length:",
                len(doc.page_content),
            )

            print(
                "Compressed length:",
                len(result),
            )

        print()
        print("=" * 80)
        print("CONTEXT COMPRESSION COMPLETE")
        print("=" * 80)

        print(
            "Output Documents:",
            len(compressed),
        )

        return compressed
