from typing import Dict
import cv2
import pytesseract


def ocr_image(image_path: str) -> Dict:
    """Run OCR over an image and return text and raw boxes."""
    img = cv2.imread(image_path)
    if img is None:
        return {"path": image_path, "text": "", "boxes": {}}
    data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
    text = " ".join([w for w in data.get("text", []) if str(w).strip()])
    return {"path": image_path, "text": text, "boxes": data}
