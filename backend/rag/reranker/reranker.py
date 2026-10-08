import logging
import os

logger = logging.getLogger(__name__)


class Reranker:
    _model = None

    @classmethod
    def model(cls):
        if cls._model is None:
            if os.getenv("EMBEDDING_BACKEND") == "onnx":
                from fastembed.rerank.cross_encoder import TextCrossEncoder

                cls._model = TextCrossEncoder(
                    model_name="Xenova/ms-marco-MiniLM-L-6-v2", threads=1,
                    cache_dir=os.getenv("FASTEMBED_CACHE_PATH"),
                )
            else:
                from sentence_transformers import CrossEncoder

                cls._model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
        return cls._model

    @classmethod
    def rerank(cls, question, documents, top_k=5):
        if not documents or os.getenv("RERANK_ENABLED", "true").lower() == "false":
            return documents[:top_k]
        try:
            model = cls.model()
            if os.getenv("EMBEDDING_BACKEND") == "onnx":
                scores = list(model.rerank(question, [doc.page_content for doc in documents]))
            else:
                scores = model.predict(
                    [(question, doc.page_content) for doc in documents],
                    batch_size=8, show_progress_bar=False,
                )
            ranked = sorted(zip(scores, documents), key=lambda item: item[0], reverse=True)
            return [doc for _, doc in ranked[:top_k]]
        except Exception:
            logger.warning("Reranking unavailable; using hybrid retrieval ranking")
            return documents[:top_k]
