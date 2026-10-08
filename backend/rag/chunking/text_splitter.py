from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

from config.settings import CHUNK_OVERLAP, CHUNK_SIZE


class TextSplitter:
    """
    Splits LangChain Document objects into smaller chunks.

    Each chunk is enriched with metadata to improve
    retrieval quality and neighbour chunk retrieval.
    """

    @staticmethod
    def split_documents(
        documents: list[Document]
    ) -> list[Document]:

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            separators=[
                "\n\n",
                "\n",
                ". ",
                " ",
                ""
            ]
        )

        chunks = splitter.split_documents(
            documents
        )

        print("=" * 80)
        print("TEXT SPLITTER")
        print("=" * 80)
        print("Input Documents :", len(documents))
        print("Output Chunks   :", len(chunks))
        print("=" * 80)

        # --------------------------------------------------
        # Maintain chunk numbering separately for each PDF
        # --------------------------------------------------

        document_chunk_counter = {}

        for chunk in chunks:

            filename = chunk.metadata.get(
                "filename",
                "Unknown"
            )

            source = chunk.metadata.get(
                "source",
                filename
            )

            page = chunk.metadata.get(
                "page",
                0
            )

            # ---------------------------------------------
            # Generate chunk id per document
            # ---------------------------------------------

            chunk_id = document_chunk_counter.get(
                filename,
                0
            )

            document_chunk_counter[filename] = (
                chunk_id + 1
            )

            # ---------------------------------------------
            # Store metadata
            # ---------------------------------------------

            chunk.metadata["chunk_id"] = chunk_id
            chunk.metadata["page_number"] = page + 1
            chunk.metadata["document_name"] = filename
            chunk.metadata["source_file"] = source

            # ---------------------------------------------
            # Contextual prefix
            # ---------------------------------------------

            context = (
                f"Document: {filename}\n"
                f"Page: {page + 1}\n\n"
            )

            chunk.page_content = (
                context +
                chunk.page_content.strip()
            )

        print("Chunk metadata enriched successfully.")
        print("=" * 80)

        return chunks