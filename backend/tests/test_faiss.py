from rag.vectorstore.vector_store import VectorStore

print("=" * 80)
print("LOADING VECTOR STORE")
print("=" * 80)

vector_db = VectorStore.load_vector_store()

print("Loaded:", vector_db is not None)

print("Vector DB Type:", type(vector_db))

print("Index Size:", vector_db.index.ntotal)

print("=" * 80)
print("RUNNING SIMILARITY SEARCH")
print("=" * 80)

docs = vector_db.similarity_search(
    "Article 14",
    k=3,
)

print("Retrieved:", len(docs))

for i, doc in enumerate(docs, start=1):
    print(f"\nDocument {i}")
    print(doc.metadata)
    print(doc.page_content[:200])