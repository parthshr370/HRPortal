import json
import re
from typing import Dict, Any, Union, List
from config.openrouter_config import OpenRouterConfig
from pydantic import ValidationError
from models.resume_models import ParsedResume, PersonalInfo, Education, Experience

class ResumeParsingAgent:
    def __init__(self, api_key: str, model_name: str):
        if not api_key:
            raise ValueError("API key is required")
        if not model_name:
            raise ValueError("Model name is required")
            
        self.api_key = api_key
        self.model_name = model_name
        self.openrouter = OpenRouterConfig()
        self.model_config = self.openrouter.get_model_config('non_reasoning')
        
        # Load the prompt template
        try:
            with open('prompts/resume_parsing_prompt.txt', 'r') as file:
                self.prompt_template = file.read()
        except Exception as e:
            raise Exception(f"Error loading prompt template: {str(e)}")

    def parse_resume(self, resume_text: str) -> ParsedResume:
        """Parse the resume text and return structured data"""
        try:
            if not resume_text or not resume_text.strip():
                raise ValueError("Resume text is empty")
                
            print("\nFormatting messages for OpenRouter...")
            messages = self.openrouter.format_messages(
                system_prompt=self.prompt_template,
                user_content=resume_text
            )
            
            print("\nMaking request to OpenRouter...")
            response = self.openrouter.make_request(
                messages=messages,
                model=self.model_name,
                api_key=self.api_key,
                temperature=self.model_config['temperature'],
                max_tokens=self.model_config['max_tokens']
            )
            
            print("\nResponse received from OpenRouter.")
            
            print("\nExtracting completion...")
            template_output = self.openrouter.get_completion(response)
            
            print("\nConverting template format to JSON...")
            print("Template output excerpt:")
            print(template_output[:500] + "..." if len(template_output) > 500 else template_output)
            
            # Convert the template format to structured JSON
            structured_data = self.convert_template_to_json(template_output)
            
            print("\nValidating structured data...")
            # Validation now happens during Pydantic instantiation
            # if not self.validate_structured_data(structured_data):
            #     print("\nWARNING: Structured data validation failed, but proceeding with available data")
            
            return structured_data
            
        except ValidationError as ve:
             print(f"\nData validation error during resume parsing: {ve}")
             # Potentially log the validation error details (ve.json())
             # Decide how to handle - return empty or partially filled? Returning empty for now.
             return self.create_empty_structure()
        except Exception as e:
            print(f"\nError parsing resume: {str(e)}")
            import traceback
            traceback.print_exc()
            return self.create_empty_structure()

    def convert_template_to_json(self, template_output: str) -> ParsedResume:
        """Convert the template output format to structured JSON using Pydantic model"""
        # Initialize the dictionary structure first
        raw_data = {
            "personal_info": {
                "name": "",
                "email": "",
                "phone": "",
                "location": ""
            },
            "summary": "",
            "education": [],
            "experience": [],
            "skills": [],  # Changed to a list from a dictionary
            "certifications": [],
            "projects": []
        }
        
        try:
            # Extract personal info
            name_match = re.search(r'NAME:\s*(.*?)(?=\n)', template_output, re.IGNORECASE)
            if name_match and name_match.group(1).strip() not in ["[Full name of the candidate]", "Not provided"]:
                raw_data["personal_info"]["name"] = name_match.group(1).strip()
            
            email_match = re.search(r'EMAIL:\s*(.*?)(?=\n)', template_output, re.IGNORECASE)
            if email_match and email_match.group(1).strip() not in ["[Email address]", "Not provided"]:
                raw_data["personal_info"]["email"] = email_match.group(1).strip()
            
            phone_match = re.search(r'PHONE:\s*(.*?)(?=\n)', template_output, re.IGNORECASE)
            if phone_match and phone_match.group(1).strip() not in ["[Phone number]", "Not provided"]:
                raw_data["personal_info"]["phone"] = phone_match.group(1).strip()
            
            location_match = re.search(r'LOCATION:\s*(.*?)(?=\n)', template_output, re.IGNORECASE)
            if location_match and location_match.group(1).strip() not in ["[City, State/Country]", "Not provided"]:
                raw_data["personal_info"]["location"] = location_match.group(1).strip()
            
            # Extract summary
            summary_section = re.search(r'SUMMARY:\s*\n(.*?)(?=\n\n|EDUCATION:)', template_output, re.DOTALL | re.IGNORECASE)
            if summary_section and summary_section.group(1).strip() not in ["[Brief professional summary]", "Not provided"]:
                raw_data["summary"] = summary_section.group(1).strip()
            
            # Extract education
            education_section = re.search(r'EDUCATION:\s*\n(.*?)(?=\n\n|EXPERIENCE:)', template_output, re.DOTALL | re.IGNORECASE)
            if education_section:
                edu_text = education_section.group(1)
                edu_entries = re.finditer(r'-\s*(.*?)\s*\|\s*(.*?)\s*\|\s*(.*?)(?=\n|$)', edu_text)
                
                for entry in edu_entries:
                    degree = entry.group(1).strip()
                    institution = entry.group(2).strip()
                    graduation_date = entry.group(3).strip()
                    
                    # Look for field and GPA
                    entry_pos = entry.end()
                    next_entry_pos = edu_text.find('-', entry_pos)
                    if next_entry_pos == -1:
                        next_entry_pos = len(edu_text)
                    
                    entry_details = edu_text[entry_pos:next_entry_pos]
                    
                    field = ""
                    field_match = re.search(r'\*\s*Field:\s*(.*?)(?=\n|\*|$)', entry_details)
                    if field_match:
                        field = field_match.group(1).strip()
                    
                    # FIX: Handle GPA - set to None if empty string
                    gpa = None
                    gpa_match = re.search(r'\*\s*GPA:\s*(.*?)(?=\n|\*|$)', entry_details)
                    if gpa_match:
                        gpa_value = gpa_match.group(1).strip()
                        if gpa_value and gpa_value not in ["Not provided", "None listed"]:
                            try:
                                # Try to convert to float, set to None if fails
                                gpa = float(gpa_value) if gpa_value else None
                            except ValueError:
                                gpa = None
                    
                    raw_data["education"].append({
                        "institution": institution,
                        "degree": degree,
                        "field": field,
                        "graduation_date": graduation_date,
                        "gpa": gpa  # Now properly handled
                    })
            
            # Extract experience
            experience_section = re.search(r'EXPERIENCE:\s*\n(.*?)(?=\n\n|SKILLS:)', template_output, re.DOTALL | re.IGNORECASE)
            if experience_section:
                exp_text = experience_section.group(1)
                exp_entries = re.finditer(r'-\s*(.*?)\s*\|\s*(.*?)\s*\|\s*(.*?)(?=\n|$)', exp_text)
                
                for entry in exp_entries:
                    title = entry.group(1).strip()
                    company = entry.group(2).strip()
                    dates = entry.group(3).strip()
                    
                    # Split dates into start and end
                    start_date = ""
                    end_date = ""
                    if "-" in dates:
                        date_parts = dates.split("-")
                        start_date = date_parts[0].strip()
                        end_date = date_parts[1].strip()
                    else:
                        start_date = dates
                        end_date = "Present"
                    
                    # Look for location and responsibilities
                    entry_pos = entry.end()
                    next_entry_pos = exp_text.find('-', entry_pos)
                    if next_entry_pos == -1:
                        next_entry_pos = len(exp_text)
                    
                    entry_details = exp_text[entry_pos:next_entry_pos]
                    
                    location = ""
                    location_match = re.search(r'\*\s*Location:\s*(.*?)(?=\n|\*|$)', entry_details)
                    if location_match:
                        location = location_match.group(1).strip()
                    
                    # Extract responsibilities
                    responsibilities = []
                    for line in entry_details.split('\n'):
                        line = line.strip()
                        if line.startswith('*') and not line.startswith('* Location:'):
                            resp = line[1:].strip()
                            if resp:
                                responsibilities.append(resp)
                    
                    raw_data["experience"].append({
                        "company": company,
                        "title": title,
                        "location": location,
                        "start_date": start_date,
                        "end_date": end_date,
                        "responsibilities": responsibilities,
                        "achievements": []  # We'll use responsibilities for both in this format
                    })
            
            # Extract skills - FIX: Convert from dictionary to list structure
            technical_skills = []
            soft_skills = []
            
            skills_section = re.search(r'SKILLS:\s*\n(.*?)(?=\n\n|PROJECTS:|CERTIFICATIONS:|ADDITIONAL INFO:|$)', template_output, re.DOTALL | re.IGNORECASE)
            if skills_section:
                skills_text = skills_section.group(1)
                
                tech_skills_match = re.search(r'Technical:\s*(.*?)(?=\n|Soft:|$)', skills_text, re.IGNORECASE)
                if tech_skills_match:
                    tech_skills = tech_skills_match.group(1).strip()
                    if tech_skills and tech_skills not in ["[List all technical skills]", "Not provided", "None listed"]:
                        technical_skills = [skill.strip() for skill in tech_skills.split(',')]
                
                soft_skills_match = re.search(r'Soft:\s*(.*?)(?=\n|$)', skills_text, re.IGNORECASE)
                if soft_skills_match:
                    soft_skills = soft_skills_match.group(1).strip()
                    if soft_skills and soft_skills not in ["[List all soft skills]", "Not provided", "None listed"]:
                        soft_skills = [skill.strip() for skill in soft_skills.split(',')]
            
            # FIX: Combine technical and soft skills into a single list
            raw_data["skills"] = technical_skills + soft_skills
            
            # Extract projects
            projects_section = re.search(r'PROJECTS:\s*\n(.*?)(?=\n\n|CERTIFICATIONS:|ADDITIONAL INFO:|$)', template_output, re.DOTALL | re.IGNORECASE)
            if projects_section:
                proj_text = projects_section.group(1)
                proj_entries = re.finditer(r'-\s*(.*?)(?:\s*\|\s*(.*?))?(?=\n|$)', proj_text)
                
                for entry in proj_entries:
                    name = entry.group(1).strip()
                    project_type = ""
                    if entry.group(2):
                        project_type = entry.group(2).strip()
                    
                    # Look for description and technologies
                    entry_pos = entry.end()
                    next_entry_pos = proj_text.find('-', entry_pos)
                    if next_entry_pos == -1:
                        next_entry_pos = len(proj_text)
                    
                    entry_details = proj_text[entry_pos:next_entry_pos]
                    
                    description = ""
                    technologies = []
                    url = ""
                    
                    # Find the first * which should be the description
                    desc_match = re.search(r'\*\s*(.*?)(?=\n\s*\*|$)', entry_details)
                    if desc_match:
                        description = desc_match.group(1).strip()
                    
                    # Find technologies
                    tech_match = re.search(r'\*\s*Technologies:\s*(.*?)(?=\n|\*|$)', entry_details)
                    if tech_match:
                        tech_list = tech_match.group(1).strip()
                        if tech_list:
                            technologies = [tech.strip() for tech in tech_list.split(',')]
                    
                    # Find URL
                    url_match = re.search(r'\*\s*URL:\s*(.*?)(?=\n|\*|$)', entry_details)
                    if url_match:
                        url = url_match.group(1).strip()
                    
                    # Only add if we have a name
                    if name and name not in ["[Project name]", "Not provided", "None listed"]:
                        raw_data["projects"].append({
                            "name": name + (" | " + project_type if project_type else ""),
                            "description": description,
                            "technologies": technologies,
                            "url": url
                        })
            
            # Extract certifications
            cert_section = re.search(r'CERTIFICATIONS:\s*\n(.*?)(?=\n\n|ADDITIONAL INFO:|$)', template_output, re.DOTALL | re.IGNORECASE)
            if cert_section:
                cert_text = cert_section.group(1)
                cert_entries = re.finditer(r'-\s*(.*?)\s*\|\s*(.*?)\s*\|\s*(.*?)(?=\n|$)', cert_text)
                
                for entry in cert_entries:
                    name = entry.group(1).strip()
                    issuer = entry.group(2).strip()
                    date = entry.group(3).strip()
                    
                    if name and name not in ["[Certification name]", "Not provided", "None listed"]:
                        raw_data["certifications"].append({
                            "name": name,
                            "issuer": issuer,
                            "date": date
                        })
            
            # Pre-validate and fix common issues before Pydantic validation
            self._fix_validation_issues(raw_data)
            
            # Instantiate Pydantic model from the dictionary
            try:
                parsed_resume_obj = ParsedResume(**raw_data)
                print("\nSuccessfully created ParsedResume from extracted data")
                return parsed_resume_obj
            except ValidationError as ve:
                print(f"Error validating parsed resume data: {ve}")
                # Try to fix the validation errors
                self._fix_validation_errors(raw_data, ve)
                # Try again with the fixed data
                parsed_resume_obj = ParsedResume(**raw_data)
                return parsed_resume_obj
            
        except Exception as e:
            print(f"Error converting template to JSON: {str(e)}")
            import traceback
            traceback.print_exc()
            # Return an empty model instance in case of regex/extraction errors
            return self.create_empty_structure()
    
    def _fix_validation_issues(self, data: Dict[str, Any]) -> None:
        """Pre-emptively fix common validation issues in the extracted data"""
        # Fix education entries
        for edu in data.get("education", []):
            # Fix GPA field
            if "gpa" in edu and (edu["gpa"] == "" or edu["gpa"] is None):
                edu["gpa"] = None
        
        # Ensure skills is a list, not a dict
        if isinstance(data.get("skills"), dict):
            technical = data["skills"].get("technical", [])
            soft = data["skills"].get("soft", [])
            data["skills"] = technical + soft
    
    def _fix_validation_errors(self, data: Dict[str, Any], validation_error: ValidationError) -> None:
        """Fix data based on specific validation errors"""
        errors = validation_error.errors()
        
        for error in errors:
            loc = error.get('loc', ())
            type_error = error.get('type', '')
            
            # Fix GPA validation errors in education entries
            if len(loc) >= 2 and loc[0] == 'education' and isinstance(loc[1], int) and 'gpa' in loc:
                if 'float_parsing' in type_error:
                    if loc[1] < len(data['education']):
                        data['education'][loc[1]]['gpa'] = None
            
            # Fix skills structure errors
            if loc and loc[0] == 'skills' and 'list_type' in type_error:
                if isinstance(data.get('skills'), dict):
                    technical = data['skills'].get('technical', [])
                    soft = data['skills'].get('soft', [])
                    data['skills'] = technical + soft

    def create_empty_structure(self) -> ParsedResume:
        """Create an empty resume structure using Pydantic model"""
        return ParsedResume(
            personal_info=PersonalInfo(
                name="",
                email=""
            ),
            education=[],
            experience=[],
            skills=[]
        )