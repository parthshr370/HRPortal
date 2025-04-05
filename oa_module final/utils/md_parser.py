# utils/md_parser.py

import re

class MarkdownParser:
    """Ultra-simplified utility that just extracts raw text from markdown"""
    
    @staticmethod
    def extract_raw_text(content: str) -> str:
        """
        Extract raw text from markdown, removing markdown syntax elements
        """
        # Remove code blocks
        content = re.sub(r'```.*?```', '', content, flags=re.DOTALL)
        
        # Remove inline code
        content = re.sub(r'`.*?`', '', content)
        
        # Remove images
        content = re.sub(r'!\[.*?\]\(.*?\)', '', content)
        
        # Remove links but keep the text
        content = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', content)
        
        # Remove HTML tags
        content = re.sub(r'<.*?>', '', content)
        
        return content.strip()