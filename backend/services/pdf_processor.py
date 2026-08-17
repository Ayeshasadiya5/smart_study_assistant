import os
import re
import uuid
import fitz
from config import Config


def clean_text(text):
    """Clean extracted PDF text."""
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^\w\s.,;:!?()\-\'\"/\n]', '', text)
    return text.strip()


def extract_text_from_pdf(filepath):
    """Extract text from PDF with page numbers."""
    chunks = []
    try:
        doc = fitz.open(filepath)
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text()
            cleaned = clean_text(text)
            if cleaned and len(cleaned) > 30:
                chunks.append({
                    'text': cleaned,
                    'page': page_num + 1,
                })
        doc.close()
    except Exception as e:
        raise ValueError(f'Failed to extract text from PDF: {str(e)}')
    return chunks


def generate_safe_filename(original_filename):
    """Generate a safe filename to prevent path traversal."""
    ext = os.path.splitext(original_filename)[1].lower()
    if ext != '.pdf':
        raise ValueError('Only PDF files are allowed.')
    safe_name = f'{uuid.uuid4().hex}{ext}'
    return safe_name


def validate_pdf_file(file):
    """Validate uploaded PDF file."""
    if not file or file.filename == '':
        raise ValueError('No file selected.')

    ext = os.path.splitext(file.filename)[1].lower()
    if ext != '.pdf':
        raise ValueError('Only PDF files are allowed.')

    if hasattr(file, 'content_type') and file.content_type:
        allowed_types = ['application/pdf', 'application/x-pdf']
        if file.content_type not in allowed_types:
            raise ValueError('Invalid file type. Only PDF files are allowed.')

    file.seek(0, os.SEEK_END)
    size = file.tell()
    file.seek(0)
    if size > Config.MAX_CONTENT_LENGTH:
        raise ValueError(f'File too large. Maximum size is {Config.MAX_CONTENT_LENGTH // (1024*1024)} MB.')

    return True
