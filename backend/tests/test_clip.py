import torch

print(torch.__version__)

print("FAISS OK")

import open_clip

print("OpenCLIP imported")

model, _, preprocess = open_clip.create_model_and_transforms(
    "ViT-B-32",
    pretrained="openai"
)

print("SUCCESS")