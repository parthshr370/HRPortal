#!/usr/bin/env python3
"""
Test script for the template-based resume parser
Usage: python test_template_parser.py path/to/resume.txt
"""

import sys
import os
import json
from config.config import MODELS
from utils.file_handlers import FileHandler
from utils.text_preprocessing import TextPreprocessor
from agents.resume_parsing_agent import ResumeParsingAgent

def test_template_parser(resume_path):
    try:
        print(f"Testing template parser with file: {resume_path}")
        
        # Initialize components
        file_handler = FileHandler()
        text_preprocessor = TextPreprocessor()
        
        # Extract and clean resume text
        print("Extracting text from resume...")
        resume_text = file_handler.extract_text(resume_path)
        print(f"Extracted {len(resume_text)} characters")
        
        # Save raw text for reference
        with open("raw_resume.txt", "w") as f:
            f.write(resume_text)
        print("Raw resume text saved to 'raw_resume.txt'")
        
        cleaned_resume_text = text_preprocessor.clean_text(resume_text)
        print(f"Cleaned text: {len(cleaned_resume_text)} characters")
        
        # Initialize resume parsing agent
        print("Initializing resume parsing agent...")
        resume_parser = ResumeParsingAgent(
            api_key=MODELS['non_reasoning']['api_key'],
            model_name=MODELS['non_reasoning']['name']
        )
        
        # Parse resume
        print("Parsing resume...")
        parsed_resume = resume_parser.parse_resume(cleaned_resume_text)
        
        # Output result
        print("\nParsed Resume:")
        pretty_json = json.dumps(parsed_resume, indent=2)
        print(pretty_json)
        
        # Save output to file
        with open("parsed_resume.json", "w") as f:
            f.write(pretty_json)
        print("\nParsed resume saved to 'parsed_resume.json'")
        
        # Check parsed data
        print("\nChecking parsed data:")
        check_parsed_data(parsed_resume)
        
        return parsed_resume
        
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()

def check_parsed_data(data):
    """Check if the parsed data has the expected fields filled"""
    # Personal info
    if data["personal_info"]["name"]:
        print(f"✓ Name: {data['personal_info']['name']}")
    else:
        print("✗ Name: Missing")
    
    if data["personal_info"]["email"]:
        print(f"✓ Email: {data['personal_info']['email']}")
    else:
        print("✗ Email: Missing")
    
    if data["personal_info"]["phone"]:
        print(f"✓ Phone: {data['personal_info']['phone']}")
    else:
        print("✗ Phone: Missing")
    
    # Check education
    if data["education"]:
        print(f"✓ Education: {len(data['education'])} entries")
        for edu in data["education"]:
            print(f"  - {edu['degree']} at {edu['institution']}")
    else:
        print("✗ Education: No entries found")
    
    # Check experience
    if data["experience"]:
        print(f"✓ Experience: {len(data['experience'])} entries")
        for exp in data["experience"]:
            print(f"  - {exp['title']} at {exp['company']}")
    else:
        print("✗ Experience: No entries found")
    
    # Check skills
    if data["skills"]["technical"]:
        print(f"✓ Technical Skills: {len(data['skills']['technical'])} found")
    else:
        print("✗ Technical Skills: None found")
    
    if data["skills"]["soft"]:
        print(f"✓ Soft Skills: {len(data['skills']['soft'])} found")
    else:
        print("✗ Soft Skills: None found")
    
    # Check projects
    if data["projects"]:
        print(f"✓ Projects: {len(data['projects'])} found")
        for proj in data["projects"]:
            print(f"  - {proj['name']}")
    else:
        print("✗ Projects: None found")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_template_parser.py path/to/resume.txt")
        sys.exit(1)
    
    resume_path = sys.argv[1]
    test_template_parser(resume_path)