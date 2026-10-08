from pathlib import Path

import fitz


class ImageExtractor:

    @staticmethod
    def extract_images(pdf_path: str):

        output = Path("data/images") / Path(pdf_path).stem
        output.mkdir(parents=True, exist_ok=True)

        doc = fitz.open(pdf_path)

        images = []

        for page_no in range(len(doc)):

            page = doc.load_page(page_no)

            for index, img in enumerate(page.get_images(full=True)):

                xref = img[0]

                pix = fitz.Pixmap(doc, xref)

                if pix.n < 5:
                    image_path = output / f"page_{page_no+1}_{index}.png"
                    pix.save(image_path)
                else:
                    pix = fitz.Pixmap(fitz.csRGB, pix)
                    image_path = output / f"page_{page_no+1}_{index}.png"
                    pix.save(image_path)

                images.append({
                    "page": page_no + 1,
                    "path": str(image_path)
                })

        doc.close()

        return images