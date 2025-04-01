# Text cleaning utilities

import re

class TextPreprocessor:
    @staticmethod
    def clean_text(text):
        """
        Clean and normalize extracted text
        """
        # Remove multiple spaces
        text = re.sub(r'\s+', ' ', text)
        
        # Remove multiple newlines
        text = re.sub(r'\n\s*\n', '\n\n', text)
        
        # Remove special characters except basic punctuation
        text = re.sub(r'[^\w\s.,;:!?()-]', '', text)
        
        # Convert multiple periods to single period
        text = re.sub(r'\.+', '.', text)
        
        return text.strip()

    @staticmethod
    def extract_sections(text):
        """
        Attempt to identify and separate resume sections
        """
        sections = {
            'education': '',
            'experience': '',
            'skills': '',
            'summary': '',
            'contact': '',
            'other': ''
        }
        
        # Simple section detection based on common headers
        education_pattern = r'(?i)(education|academic|qualification)'
        experience_pattern = r'(?i)(experience|work history|employment)'
        skills_pattern = r'(?i)(skills|technical skills|competencies)'
        summary_pattern = r'(?i)(summary|profile|objective)'
        
        lines = text.split('\n')
        current_section = 'other'
        
        for line in lines:
            if re.search(education_pattern, line, re.IGNORECASE):
                current_section = 'education'
            elif re.search(experience_pattern, line, re.IGNORECASE):
                current_section = 'experience'
            elif re.search(skills_pattern, line, re.IGNORECASE):
                current_section = 'skills'
            elif re.search(summary_pattern, line, re.IGNORECASE):
                current_section = 'summary'
            elif re.search(r'(?i)(contact|email|phone|address)', line):
                current_section = 'contact'
            
            sections[current_section] += line + '\n'
        
        return {k: v.strip() for k, v in sections.items()}