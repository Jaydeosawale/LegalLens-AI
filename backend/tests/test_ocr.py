from rag.ocr.ocr_service import OCRService

text = OCRService.extract(
       "data/images/India-constitution-preamble.svg.png"

)

print(text)