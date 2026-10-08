"""
=========================================================
LegalLens AI
Image Embedding Service
=========================================================
"""

from pathlib import Path
import threading

import numpy as np
import torch
from PIL import Image
from transformers import AutoModel, AutoProcessor

from config.settings import VISION_MODEL


class ImageEmbeddingService:
    """
    Singleton SigLIP2 Image Embedding Service.

    Supports

    • Image Embeddings
    • Batch Image Embeddings
    • Text Embeddings

    Future

    • Video Embeddings
    • Multimodal Retrieval
    """

    _processor = None
    _model = None
    _device = None
    _lock = threading.Lock()

    MODEL_NAME = VISION_MODEL

    @classmethod
    def load_model(cls):

        if cls._model is not None:
            return cls._processor, cls._model

        with cls._lock:

            if cls._model is not None:
                return cls._processor, cls._model

            print("=" * 80)
            print("LOADING SIGLIP2")
            print("=" * 80)

            if torch.backends.mps.is_available():
                cls._device = "mps"

            elif torch.cuda.is_available():
                cls._device = "cuda"

            else:
                cls._device = "cpu"

            print("Device :", cls._device)

            cls._processor = AutoProcessor.from_pretrained(
                cls.MODEL_NAME
            )

            cls._model = AutoModel.from_pretrained(
                cls.MODEL_NAME
            )

            cls._model.to(cls._device)
            cls._model.eval()

            print("SigLIP2 Ready")
            print("=" * 80)

        return cls._processor, cls._model

    @classmethod
    def embed_image(cls, image_path):

        image_path = Path(image_path)

        if not image_path.exists():
            raise FileNotFoundError(image_path)

        processor, model = cls.load_model()

        image = Image.open(image_path).convert("RGB")

        inputs = processor(
            images=image,
            return_tensors="pt",
        )

        inputs = {
            key: value.to(cls._device)
            for key, value in inputs.items()
        }

        with torch.no_grad():

            features = model.get_image_features(
                **inputs
            )

        features = torch.nn.functional.normalize(
            features,
            dim=-1,
        )

        return (
            features.squeeze()
            .cpu()
            .numpy()
            .astype(np.float32)
        )

    @classmethod
    def embed_images(cls, image_paths):

        embeddings = []

        for image_path in image_paths:

            embeddings.append(
                cls.embed_image(image_path)
            )

        return embeddings

    @classmethod
    def embed_text(cls, text):

        processor, model = cls.load_model()

        inputs = processor(
            text=text,
            return_tensors="pt",
            padding=True,
        )

        inputs = {
            key: value.to(cls._device)
            for key, value in inputs.items()
        }

        with torch.no_grad():

            features = model.get_text_features(
                **inputs
            )

        features = torch.nn.functional.normalize(
            features,
            dim=-1,
        )

        return (
            features.squeeze()
            .cpu()
            .numpy()
            .astype(np.float32)
        )