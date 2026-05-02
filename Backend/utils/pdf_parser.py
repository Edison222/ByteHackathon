from pypdf import PdfReader
from pdf2image import convert_from_bytes
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r"C:/Program Files/Tesseract-OCR/tesseract.exe"
POPPLER_PATH = r"C:/poppler/poppler-25.12.0/Library/bin"

def extract_text_from_pdf(file_stream):
    try:
        file_stream.seek(0)

        reader = PdfReader(file_stream)
        extracted_pages = []

        for i, page in enumerate(reader.pages, start=1):
            text = page.extract_text()
            if text and text.strip():
                extracted_pages.append(f"[Page {i}]\n{text}")

        if len("".join(extracted_pages)) > 100:
            return "\n\n".join(extracted_pages).strip()

        file_stream.seek(0)

        images = convert_from_bytes(
            file_stream.read(),
            poppler_path=POPPLER_PATH
        )

        ocr_pages = []

        for i, image in enumerate(images, start=1):
            text = pytesseract.image_to_string(image)
            if text and text.strip():
                ocr_pages.append(f"[Page {i} OCR]\n{text}")

        return "\n\n".join(ocr_pages).strip()

    except Exception as e:
        raise ValueError(f"Failed to extract text from PDF: {str(e)}")