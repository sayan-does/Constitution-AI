import io
import pymupdf
import docx
import easyocr
from config import DOCUMENTS_DIR
import uuid
import os

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
        """Process document based on file type"""
        type_map = {
            'pdf': cls.extract_text_from_pdf,
            'docx': cls.extract_text_from_docx, 
            'jpg': cls.extract_text_from_image,
            'jpeg': cls.extract_text_from_image,
            'png': cls.extract_text_from_image,
            'image': cls.extract_text_from_image
        }
        
        if file_type not in type_map:
            raise ValueError(f"Unsupported file type: {file_type}")
        
        return type_map[file_type](file)
        
    @classmethod
    def process_directory_documents(cls):
        """Process all documents in the DOCUMENTS_DIR"""
        processed_texts = []
        
        if not DOCUMENTS_DIR.exists():
            DOCUMENTS_DIR.mkdir(parents=True, exist_ok=True)
            return processed_texts
            
        for file_path in DOCUMENTS_DIR.glob('**/*'):
            if file_path.is_file():
                file_type = file_path.suffix.lower().replace('.', '')
                
                # Skip unsupported file types
                if file_type not in ['pdf', 'docx', 'jpg', 'jpeg', 'png']:
                    continue
                    
                try:
                    with open(file_path, 'rb') as f:
                        file_content = f.read()
                    
                    text = cls.process_document(file_content, file_type)
                    processed_texts.append(text)
                    print(f"Processed: {file_path.name}")
                except Exception as e:
                    print(f"Error processing {file_path.name}: {str(e)}")
                    
        return processed_texts