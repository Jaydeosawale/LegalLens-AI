class CitationService:

    @staticmethod
    def build(documents):

        citations = []

        seen = set()

        for doc in documents:

            filename = doc.metadata.get(
                "filename",
                "Unknown"
            )

            page = doc.metadata.get(
                "page",
                0
            ) + 1

            key = (
                filename,
                page
            )

            if key in seen:
                continue

            seen.add(key)

            citations.append(
                {
                    "filename": filename,
                    "page": page
                }
            )

        return citations