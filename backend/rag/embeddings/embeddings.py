import os
import threading

from langchain_core.embeddings import Embeddings


class SentenceTransformerEmbeddings(Embeddings):
    def __init__(self):
        self.backend = os.getenv("EMBEDDING_BACKEND", "sentence_transformers")
        model_name = "sentence-transformers/all-MiniLM-L6-v2"
        if self.backend == "onnx":
            from fastembed import TextEmbedding

            self.model = TextEmbedding(
                model_name=model_name,
                cache_dir=os.getenv("FASTEMBED_CACHE_PATH"),
                threads=1,
            )
        elif self.backend == "sentence_transformers":
            import torch
            from sentence_transformers import SentenceTransformer

            torch.set_num_threads(1)
            self.model = SentenceTransformer(model_name, device="cpu")
        else:
            raise ValueError("Unsupported EMBEDDING_BACKEND")

    def embed_documents(self, texts):
        if self.backend == "onnx":
            return [value.tolist() for value in self.model.embed(texts, batch_size=8)]
        return self.model.encode(
            texts, normalize_embeddings=True, convert_to_numpy=True,
            show_progress_bar=False, batch_size=8,
        ).tolist()

    def embed_query(self, text):
        return self.embed_documents([text])[0]


class EmbeddingModel:
    _model = None
    _lock = threading.Lock()

    @classmethod
    def get_model(cls):
        with cls._lock:
            if cls._model is None:
                cls._model = SentenceTransformerEmbeddings()
            return cls._model
