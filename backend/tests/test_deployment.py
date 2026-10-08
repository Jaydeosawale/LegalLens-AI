import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import fitz
from langchain_core.documents import Document

from ingestion.document_loader import DocumentLoader
from rag.reranker.reranker import Reranker


class DeploymentTest(unittest.TestCase):
    def create_pdf(self, path, content):
        with fitz.open() as pdf:
            page = pdf.new_page()
            page.insert_text((72, 72), content)
            pdf.save(path)

    def test_same_filename_cannot_reuse_another_document_text(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for folder, content in [("first", "Notice is thirty days."), ("second", "Notice is sixty days.")]:
                (root / folder).mkdir()
                self.create_pdf(root / folder / "agreement.pdf", content)
            first = DocumentLoader.load_pdf(str(root / "first" / "agreement.pdf"))
            second = DocumentLoader.load_pdf(str(root / "second" / "agreement.pdf"))
            self.assertIn("thirty", first[0].page_content)
            self.assertIn("sixty", second[0].page_content)
            self.assertEqual(first[0].metadata["page"], 1)
            self.assertNotIn(directory, first[0].metadata["source"])

    def test_low_memory_mode_preserves_hybrid_ranking(self):
        documents = [Document(page_content="first"), Document(page_content="second")]
        with patch.dict(os.environ, {"RERANK_ENABLED": "false"}):
            self.assertEqual(Reranker.rerank("notice", documents, top_k=1), documents[:1])


if __name__ == "__main__":
    unittest.main()
