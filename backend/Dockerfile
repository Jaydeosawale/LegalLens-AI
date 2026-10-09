FROM python:3.11-slim-bookworm
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 \
    EMBEDDING_BACKEND=onnx FASTEMBED_CACHE_PATH=/opt/models \
    TOKENIZERS_PARALLELISM=false RERANK_ENABLED=false MALLOC_TRIM_THRESHOLD_=131072 \
    TESSDATA_PREFIX=/usr/share/tesseract-ocr/5/tessdata OCR_LANGUAGES=eng+hin+mar
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 tesseract-ocr-eng tesseract-ocr-hin tesseract-ocr-mar \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements-deploy.txt .
RUN pip install --no-cache-dir -r requirements-deploy.txt
RUN python -c "from fastembed import TextEmbedding; TextEmbedding(model_name='sentence-transformers/all-MiniLM-L6-v2', cache_dir='/opt/models', threads=1)"
COPY . .
RUN useradd --create-home app && chown -R app:app /app /opt/models
USER app
CMD ["sh", "-c", "exec uvicorn api.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1"]
