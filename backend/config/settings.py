import os

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Keys
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Model
MODEL_NAME = os.getenv(
    "MODEL_NAME",
    "openai/gpt-oss-120b"
)
# =====================================================
# Vision
# =====================================================

VISION_MODEL = "google/siglip2-base-patch16-224"
#VISION_MODEL = "google/siglip-base-patch16-224"
VISION_BATCH_SIZE = 16

# Vector Store
VECTOR_DB_PATH = "services/vectorstore/faiss_index"

# Upload Folder
UPLOAD_FOLDER = "data/uploads"

# Chunk Settings
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200