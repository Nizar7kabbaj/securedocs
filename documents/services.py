from pathlib import Path

import pytesseract
from django.conf import settings
from pdf2image import convert_from_path
from PIL import Image

from classifier.inference import classify_text


pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_CMD

OCR_LANG = "fra+eng"


def extract_text_from_image(image_path: Path) -> str:
    """Run OCR on a single image file (JPG/PNG)."""
    image = Image.open(image_path)
    return pytesseract.image_to_string(image, lang=OCR_LANG)


def extract_text_from_pdf(pdf_path: Path) -> str:
    pages = convert_from_path(
        str(pdf_path),
        dpi=200,
        poppler_path=settings.POPPLER_BIN,
    )
    page_texts = []
    for page_image in pages:
        text = pytesseract.image_to_string(page_image, lang=OCR_LANG)
        page_texts.append(text)
    return "\n\n".join(page_texts)


def extract_text(file_path) -> str:
    
    path = Path(file_path)
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        return extract_text_from_pdf(path)
    if suffix in {".jpg", ".jpeg", ".png"}:
        return extract_text_from_image(path)
    return ""


def classify_document(file_path) -> tuple[str, str, float]:
    text = extract_text(file_path)
    label, confidence = classify_text(text)
    return text, label, confidence