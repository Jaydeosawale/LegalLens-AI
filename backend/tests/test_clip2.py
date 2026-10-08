import open_clip

print("Imports done")

model, _, preprocess = open_clip.create_model_and_transforms(
    "ViT-B-32-quickgelu",
    pretrained="openai"
)

print("SUCCESS")