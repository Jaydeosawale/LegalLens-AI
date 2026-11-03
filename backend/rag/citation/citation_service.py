"""Build source links from valid, one-based PDF metadata."""
import re


class CitationService:
    @staticmethod
    def build(documents, answer=None):
        # Explicit document references map to the numbered context given to the model.
        referenced = set()
        if answer:
            referenced = {int(value) for value in re.findall(r'\bDocument\s+(\d+)\b', answer, re.I)}
        citations = []
        seen = set()
        for index, doc in enumerate(documents, 1):
            if referenced and index not in referenced:
                continue
            metadata = doc.metadata
            filename = metadata.get('filename') or metadata.get('document_name')
            page = metadata.get('page') or metadata.get('page_number')
            if not filename or filename == 'Unknown' or isinstance(page, bool):
                continue
            try:
                page = int(page)
            except (ValueError, TypeError):
                continue
            if page < 1:
                continue
            key = (filename, page)
            if key not in seen:
                seen.add(key)
                citations.append({'filename': filename, 'page': page})
        return citations
