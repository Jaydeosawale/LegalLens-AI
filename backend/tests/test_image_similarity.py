from api.vision.image_similarity_service import (
    ImageSimilarityService,
)

results = ImageSimilarityService.search(
       "data/images/supreme court of India.jpg"
)

for item in results:

    print(item)
