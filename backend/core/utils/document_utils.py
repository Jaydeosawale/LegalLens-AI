"""
=========================================================
LegalLens AI
Document Utilities
=========================================================
"""


class DocumentUtils:
    @staticmethod
    def remove_duplicates(documents):
        unique = []
        seen = set()

        for doc in documents:
            metadata = doc.metadata

            key = (
                metadata.get(
                    "document_name",
                    metadata.get("filename", ""),
                ),
                metadata.get("chunk_id", -1),
            )

            if key in seen:
                continue

            seen.add(key)
            unique.append(doc)

        return unique
