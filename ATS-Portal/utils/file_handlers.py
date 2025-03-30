# File processing utilities

import PyPDF2
from docx import Document
import magic
import os

class FileHandler:
    @staticmethod
    def detect_file_type(file_path):
        mime = magic.Magic(mime=True)
        file_type = mime.from_file(file_path)
        return file_type

    @staticmethod
    def extract_text_from_pdf(file_path):
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text()
            return text.strip()
        except Exception as e:
            raise Exception(f"Error extracting text from PDF: {str(e)}")

    @staticmethod
    def extract_text_from_docx(file_path):
        try:
            doc = Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text.strip()
        except Exception as e:
            raise Exception(f"Error extracting text from DOCX: {str(e)}")

    @staticmethod
    def extract_text_from_txt(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read().strip()
        except Exception as e:
            raise Exception(f"Error extracting text from TXT: {str(e)}")

    @staticmethod
    def extract_text(file_path):
        file_type = FileHandler.detect_file_type(file_path)
        
        if "pdf" in file_type:
            return FileHandler.extract_text_from_pdf(file_path)
        elif "msword" in file_type or "officedocument" in file_type:
            return FileHandler.extract_text_from_docx(file_path)
        elif "text/plain" in file_type:
            return FileHandler.extract_text_from_txt(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")