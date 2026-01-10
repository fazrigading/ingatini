import io
from typing import Optional

try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None

try:
    from docx import Document as DocxDocument
except ImportError:
    DocxDocument = None


def extract_text_from_pdf(file_content: bytes) -> Optional[str]:
    """Extract text from PDF file."""
    if PdfReader is None:
        raise ImportError("pypdf is required for PDF support. Install with: pip install pypdf")
    
    try:
        pdf_reader = PdfReader(io.BytesIO(file_content))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        raise ValueError(f"Failed to extract PDF: {str(e)}")


def extract_text_from_docx(file_content: bytes) -> Optional[str]:
    """Extract text from DOCX file."""
    if DocxDocument is None:
        raise ImportError("python-docx is required for DOCX support. Install with: pip install python-docx")
    
    try:
        doc = DocxDocument(io.BytesIO(file_content))
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text
    except Exception as e:
        raise ValueError(f"Failed to extract DOCX: {str(e)}")


def extract_text_from_txt(file_content: bytes) -> str:
    """Extract text from TXT file."""
    try:
        return file_content.decode('utf-8', errors='ignore')
    except Exception as e:
        raise ValueError(f"Failed to extract TXT: {str(e)}")


def extract_text_from_file(filename: str, file_content: bytes) -> str:
    """
    Extract text from file based on file extension.
    
    Supported formats:
    - .pdf (requires pypdf)
    - .docx (requires python-docx)
    - .txt (always supported)
    """
    filename_lower = filename.lower()
    
    if filename_lower.endswith('.pdf'):
        return extract_text_from_pdf(file_content)
    elif filename_lower.endswith('.docx'):
        return extract_text_from_docx(file_content)
    elif filename_lower.endswith('.txt'):
        return extract_text_from_txt(file_content)
    else:
        raise ValueError(f"Unsupported file format: {filename}")
