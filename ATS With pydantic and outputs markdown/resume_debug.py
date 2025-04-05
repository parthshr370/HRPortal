#!/usr/bin/env python3
"""
Resume Parser Debugging Tool
Usage: python resume_debug.py path/to/resume.pdf
"""

import sys
import os
import json
from config.config import MODELS
from utils.file_handlers import FileHandler
from utils.text_preprocessing import TextPreprocessor
from agents.resume_parsing_agent import ResumeParsingAgent

def debug_resume_parser(resume_path):
    try:
        print(f"Debugging resume parser with file: {resume_path}")
        
        # Initialize components
        file_handler = FileHandler()
        text_preprocessor = TextPreprocessor()
        
        # Extract text from resume
        print("\n1. EXTRACTING RAW TEXT:")
        resume_text = file_handler.extract_text(resume_path)
        print(f"Extracted {len(resume_text)} characters")
        print("First 500 characters:")
        print(resume_text[:500])
        
        # Save raw text to file for inspection
        with open("debug_raw_text.txt", "w") as f:
            f.write(resume_text)
        print("\nRaw text saved to 'debug_raw_text.txt'")
        
        # Clean the text
        print("\n2. CLEANING TEXT:")
        cleaned_resume_text = text_preprocessor.clean_text(resume_text)
        print(f"Cleaned text: {len(cleaned_resume_text)} characters")
        print("First 500 characters of cleaned text:")
        print(cleaned_resume_text[:500])
        
        # Save cleaned text to file
        with open("debug_cleaned_text.txt", "w") as f:
            f.write(cleaned_resume_text)
        print("\nCleaned text saved to 'debug_cleaned_text.txt'")
        
        # Initialize resume parsing agent with verbose logging
        print("\n3. INITIALIZING RESUME PARSING AGENT:")
        resume_parser = ResumeParsingAgent(
            api_key=MODELS['non_reasoning']['api_key'],
            model_name=MODELS['non_reasoning']['name']
        )
        
        # Parse resume
        print("\n4. PARSING RESUME:")
        parsed_resume = resume_parser.parse_resume(cleaned_resume_text)
        
        # Print parsed data
        print("\n5. PARSED RESUME STRUCTURE:")
        pretty_json = json.dumps(parsed_resume, indent=2)
        print(pretty_json)
        
        # Save parsed data to file
        with open("debug_parsed_resume.json", "w") as f:
            f.write(pretty_json)
        print("\nParsed resume saved to 'debug_parsed_resume.json'")
        
        # Check for empty or missing sections
        print("\n6. VALIDATION CHECK:")
        total_fields = 0
        empty_fields = 0
        
        # Check personal info
        for key, value in parsed_resume["personal_info"].items():
            total_fields += 1
            if not value:
                empty_fields += 1
                print(f"Empty field: personal_info.{key}")
        
        # Check summary
        total_fields += 1
        if not parsed_resume["summary"]:
            empty_fields += 1
            print(f"Empty field: summary")
        
        # Check education
        if not parsed_resume["education"]:
            total_fields += 1
            empty_fields += 1
            print(f"Empty array: education")
        else:
            for i, edu in enumerate(parsed_resume["education"]):
                for key, value in edu.items():
                    total_fields += 1
                    if not value:
                        empty_fields += 1
                        print(f"Empty field: education[{i}].{key}")
        
        # Check experience
        if not parsed_resume["experience"]:
            total_fields += 1
            empty_fields += 1
            print(f"Empty array: experience")
        else:
            for i, exp in enumerate(parsed_resume["experience"]):
                for key, value in exp.items():
                    if key not in ["responsibilities", "achievements"]:
                        total_fields += 1
                        if not value:
                            empty_fields += 1
                            print(f"Empty field: experience[{i}].{key}")
                
                # Check responsibilities and achievements
                for key in ["responsibilities", "achievements"]:
                    total_fields += 1
                    if not exp.get(key, []):
                        empty_fields += 1
                        print(f"Empty array: experience[{i}].{key}")
        
        # Check skills
        for key in ["technical", "soft"]:
            total_fields += 1
            if not parsed_resume["skills"].get(key, []):
                empty_fields += 1
                print(f"Empty array: skills.{key}")
        
        # Check certifications
        if not parsed_resume["certifications"]:
            total_fields += 1
            empty_fields += 1
            print(f"Empty array: certifications")
        
        # Check if projects section exists (in our improved prompt)
        if "projects" in parsed_resume:
            if not parsed_resume["projects"]:
                total_fields += 1
                empty_fields += 1
                print(f"Empty array: projects")
        
        # Print summary
        print(f"\nSummary: {empty_fields} empty fields out of {total_fields} total fields")
        print(f"Completion percentage: {((total_fields - empty_fields) / total_fields) * 100:.2f}%")
        
        if empty_fields > total_fields / 2:
            print("\nWARNING: More than half of fields are empty, suggesting parsing issues")
        
        return parsed_resume
        
    except Exception as e:
        print(f"Error in debugging: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python resume_debug.py path/to/resume.pdf")
        sys.exit(1)
    
    resume_path = sys.argv[1]
    debug_resume_parser(resume_path)