"""
PDF processing utilities for multi-page and native PDF support
"""
import io
from typing import List, Tuple
from PIL import Image
import PyPDF2
from pdf2image import convert_from_bytes
import pytesseract

def is_pdf(file_bytes: bytes) -> bool:
    """Check if file is a PDF"""
    return file_bytes[:4] == b'%PDF'

def extract_text_from_native_pdf(pdf_bytes: bytes) -> str:
    """Extract text from native (text-based) PDF"""
    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        raise Exception(f"Failed to extract text from PDF: {str(e)}")

def convert_pdf_to_images(pdf_bytes: bytes, dpi: int = 300) -> List[Image.Image]:
    """Convert PDF pages to images for OCR"""
    try:
        images = convert_from_bytes(pdf_bytes, dpi=dpi)
        return images
    except Exception as e:
        raise Exception(f"Failed to convert PDF to images: {str(e)}")

def process_pdf(pdf_bytes: bytes) -> Tuple[str, List[Image.Image]]:
    """
    Process PDF - try native text extraction first, fall back to OCR
    Returns: (extracted_text, list_of_images)
    """
    # Try native text extraction
    try:
        text = extract_text_from_native_pdf(pdf_bytes)
        if text.strip():  # If we got meaningful text
            images = convert_pdf_to_images(pdf_bytes, dpi=150)  # Lower DPI for preview
            return text, images
    except Exception:
        pass
    
    # Fall back to OCR
    images = convert_pdf_to_images(pdf_bytes)
    text = ""
    for img in images:
        text += pytesseract.image_to_string(img) + "\n"
    
    return text, images

def get_pdf_page_count(pdf_bytes: bytes) -> int:
    """Get number of pages in PDF"""
    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
        return len(pdf_reader.pages)
    except Exception:
        return 0
