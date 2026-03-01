import os
import pdfplumber
from PIL import Image
import pytesseract
from .parse import parse_text
from ..config import settings


def extract_text_from_pdf(path: str) -> str:
    text = ""
    try:
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
    except Exception:
        text = ""
    if not text.strip() and settings.ocr_enabled:
        # render each page to image and OCR
        try:
            from pdf2image import convert_from_path
            images = convert_from_path(path)
            for img in images:
                text += pytesseract.image_to_string(img)
        except Exception:
            pass
    return text


def extract_text_from_image(path: str) -> str:
    if settings.tesseract_cmd:
        pytesseract.pytesseract.tesseract_cmd = settings.tesseract_cmd
    return pytesseract.image_to_string(Image.open(path))


def process_file(path: str) -> dict:
    ext = os.path.splitext(path)[1].lower()
    if ext in ['.pdf']:
        txt = extract_text_from_pdf(path)
    elif ext in ['.png', '.jpg', '.jpeg', '.tiff', '.bmp']:
        txt = extract_text_from_image(path)
    else:
        raise ValueError("Unsupported file type")
    return parse_text(txt)
