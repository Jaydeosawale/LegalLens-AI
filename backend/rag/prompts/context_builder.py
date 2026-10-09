"""
=========================================================
LegalLens AI
Context Builder
=========================================================
"""


class ContextBuilder:
    """
    Builds the final context supplied to the LLM.

    Combines

    • Retrieved document chunks
    • Related images
    • Uploaded image analysis
    • OCR text (already present in document chunks)
    """

    @staticmethod
    def select_documents(documents, max_bytes=12000):
        selected = []
        remaining = max_bytes
        for document in documents:
            size = len(document.page_content.encode('utf-8')) + 400
            if size <= remaining:
                selected.append(document)
                remaining -= size
        return selected

    @staticmethod
    def build(
        documents,
        image_results=None,
        image_analysis=None,
    ):

        sections = []

        # =====================================================
        # DOCUMENT CONTEXT
        # =====================================================

        document_section = []

        for i, doc in enumerate(documents, start=1):

            text = doc.page_content.strip()

            if not text:
                continue

            metadata = doc.metadata

            document_section.append(
                f"""
---------------- Document {i} ----------------

Document : {metadata.get("document_name", "")}
Page     : {metadata.get("page", metadata.get("page_number", ""))}
Chunk    : {metadata.get("chunk_id", "")}

{text}
"""
            )

        if document_section:

            sections.append(
                "\n====================================================\n"
                "DOCUMENT CONTEXT\n"
                "====================================================\n"
            )

            sections.extend(document_section)

        # =====================================================
        # RELATED IMAGES
        # =====================================================

        if image_results:

            sections.append(
                "\n====================================================\n"
                "RELATED IMAGES\n"
                "====================================================\n"
            )

            for index, image in enumerate(image_results, start=1):

                sections.append(
                    f"""
Image {index}

File       : {image.get("filename", "")}
PDF        : {image.get("pdf_name", "")}
Page       : {image.get("page", "")}
Caption    : {image.get("caption", "")}
Similarity : {image.get("score", 0):.4f}
Path       : {image.get("image_path", "")}
"""
                )

        # =====================================================
        # UPLOADED IMAGE
        # =====================================================

        if image_analysis:

            sections.append(
                "\n====================================================\n"
                "UPLOADED IMAGE ANALYSIS\n"
                "====================================================\n"
            )

            if isinstance(image_analysis, dict):

                sections.append(
                    f"""
File       : {image_analysis.get("filename", "")}
PDF        : {image_analysis.get("pdf_name", "")}
Page       : {image_analysis.get("page", "")}
Caption    : {image_analysis.get("caption", "")}
Similarity : {image_analysis.get("score", 0)}
Path       : {image_analysis.get("image_path", "")}
"""
                )

            else:

                sections.append(str(image_analysis))

        return "\n".join(sections)
