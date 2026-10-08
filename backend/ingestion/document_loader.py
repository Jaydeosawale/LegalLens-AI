import os
from pathlib import Path

import fitz
from langchain_core.documents import Document


class DocumentLoader:
    @classmethod
    def load_pdf(cls, file_path: str) -> list[Document]:
        path = Path(file_path)
        documents = []
        with fitz.open(path) as pdf:
            if pdf.needs_pass:
                raise ValueError("Unlock the PDF before uploading it.")
            if len(pdf) > 200:
                raise ValueError("Upload a PDF with 200 pages or fewer.")
            for page_index, page in enumerate(pdf):
                text = page.get_text("text").strip()
                used_ocr = not text
                if used_ocr:
                    try:
                        text_page = page.get_textpage_ocr(
                            language=os.getenv("OCR_LANGUAGES", "eng"), dpi=150,
                            full=True, tessdata=os.getenv("TESSDATA_PREFIX"),
                        )
                        text = page.get_text("text", textpage=text_page).strip()
                    except Exception as error:
                        raise ValueError("Text could not be read from the scanned PDF.") from error
                if text:
                    documents.append(Document(page_content=text, metadata={
                        "source": path.name, "filename": path.name,
                        "document_name": path.name, "page": page_index + 1,
                        "page_number": page_index + 1, "ocr": used_ocr,
                    }))
        return documents
