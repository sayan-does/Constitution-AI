import io
import pymupdf
import docx
import easyocr
from config import DOCUMENTS_DIR
import uuid

class DocumentProcessor:
    """Handles parsing and text extraction from various document types"""
    @staticmethod
    def extract_text_from_pdf(pdf_file):
        """Extract text from PDF files"""
        doc = pymupdf.open(stream=pdf_file, filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        return text

    @staticmethod
    def extract_text_from_docx(docx_file):
        """Extract text from DOCX files"""
        doc = docx.Document(docx_file)
        return "\n".join([para.text for para in doc.paragraphs])

    @staticmethod
    def extract_text_from_image(image_file):
        """Extract text from images using OCR"""
        reader = easyocr.Reader(['en'])  # English OCR
        results = reader.readtext(image_file)
        return " ".join([result[1] for result in results])

    @classmethod
    def process_document(cls, file, file_type):
        file_path = DOCUMENTS_DIR / f"doc_{uuid.uuid4()}.{file_type}"
        """Process document based on file type"""
        type_map = {
            'pdf': cls.extract_text_from_pdf,
            'docx': cls.extract_text_from_docx, 
            'image': cls.extract_text_from_image
        }
        
        if file_type not in type_map:
            raise ValueError(f"Unsupported file type: {file_type}")
        
        return type_map[file_type](file)