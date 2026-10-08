from api.vision.image_embedding_service import ImageEmbeddingService

embedding = ImageEmbeddingService.embed_image(
   "data/images/supreme court of India.jpg"
)

print(len(embedding))