import json
import re
from typing import Dict, Any
from config.openrouter_config import OpenRouterConfig

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

    def parse_resume(self, resume_text: str) -> Dict[str, Any]:
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
            if not self.validate_structured_data(structured_data):
                print("\nWARNING: Structured data validation failed, but proceeding with available data")
            
            return structured_data
            
        except Exception as e:
            print(f"\nError parsing resume: {str(e)}")
            import traceback
            traceback.print_exc()
            return self.create_empty_structure()

    def convert_template_to_json(self, template_output: str) -> Dict[str, Any]:
        """Convert the template output format to structured JSON"""
        # Initialize the structure
        result = {
            "personal_info": {
                "name": "",
                "email": "",
                "phone": "",
                "location": ""
            },
            "summary": "",
            "education": [],
            "experience": [],
            "skills": {
                "technical": [],
                "soft": []
            },
            "certifications": [],
            "projects": []
        }
        
        try:
            # Extract personal info
            name_match = re.search(r'NAME:\s*(.*?)(?=\n)', template_output, re.IGNORECASE)
            if name_match and name_match.group(1).strip() not in ["[Full name of the candidate]", "Not provided"]:
                result["personal_info"]["name"] = name_match.group(1).strip()
            
            email_match = re.search(r'EMAIL:\s*(.*?)(?=\n)', template_output, re.IGNORECASE)
            if email_match and email_match.group(1).strip() not in ["[Email address]", "Not provided"]:
                result["personal_info"]["email"] = email_match.group(1).strip()
            
            phone_match = re.search(r'PHONE:\s*(.*?)(?=\n)', template_output, re.IGNORECASE)
            if phone_match and phone_match.group(1).strip() not in ["[Phone number]", "Not provided"]:
                result["personal_info"]["phone"] = phone_match.group(1).strip()
            
            location_match = re.search(r'LOCATION:\s*(.*?)(?=\n)', template_output, re.IGNORECASE)
            if location_match and location_match.group(1).strip() not in ["[City, State/Country]", "Not provided"]:
                result["personal_info"]["location"] = location_match.group(1).strip()
            
            # Extract summary
            summary_section = re.search(r'SUMMARY:\s*\n(.*?)(?=\n\n|EDUCATION:)', template_output, re.DOTALL | re.IGNORECASE)
            if summary_section and summary_section.group(1).strip() not in ["[Brief professional summary]", "Not provided"]:
                result["summary"] = summary_section.group(1).strip()
            
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
                    
                    gpa = ""
                    gpa_match = re.search(r'\*\s*GPA:\s*(.*?)(?=\n|\*|$)', entry_details)
                    if gpa_match:
                        gpa = gpa_match.group(1).strip()
                    
                    result["education"].append({
                        "institution": institution,
                        "degree": degree,
                        "field": field,
                        "graduation_date": graduation_date,
                        "gpa": gpa
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
                    
                    result["experience"].append({
                        "company": company,
                        "title": title,
                        "location": location,
                        "start_date": start_date,
                        "end_date": end_date,
                        "responsibilities": responsibilities,
                        "achievements": []  # We'll use responsibilities for both in this format
                    })
            
            # Extract skills
            skills_section = re.search(r'SKILLS:\s*\n(.*?)(?=\n\n|PROJECTS:|CERTIFICATIONS:|ADDITIONAL INFO:|$)', template_output, re.DOTALL | re.IGNORECASE)
            if skills_section:
                skills_text = skills_section.group(1)
                
                tech_skills_match = re.search(r'Technical:\s*(.*?)(?=\n|Soft:|$)', skills_text, re.IGNORECASE)
                if tech_skills_match:
                    tech_skills = tech_skills_match.group(1).strip()
                    if tech_skills and tech_skills not in ["[List all technical skills]", "Not provided", "None listed"]:
                        result["skills"]["technical"] = [skill.strip() for skill in tech_skills.split(',')]
                
                soft_skills_match = re.search(r'Soft:\s*(.*?)(?=\n|$)', skills_text, re.IGNORECASE)
                if soft_skills_match:
                    soft_skills = soft_skills_match.group(1).strip()
                    if soft_skills and soft_skills not in ["[List all soft skills]", "Not provided", "None listed"]:
                        result["skills"]["soft"] = [skill.strip() for skill in soft_skills.split(',')]
            
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
                        result["projects"].append({
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
                        result["certifications"].append({
                            "name": name,
                            "issuer": issuer,
                            "date": date
                        })
            
            return result
            
        except Exception as e:
            print(f"Error converting template to JSON: {str(e)}")
            import traceback
            traceback.print_exc()
            return self.create_empty_structure()

    def create_empty_structure(self) -> Dict[str, Any]:
        """Create an empty resume structure"""
        return {
            "personal_info": {
                "name": "",
                "email": "",
                "phone": "",
                "location": ""
            },
            "summary": "",
            "education": [],
            "experience": [],
            "skills": {
                "technical": [],
                "soft": []
            },
            "certifications": [],
            "projects": []
        }

    def validate_structured_data(self, data: Dict[str, Any]) -> bool:
        """Validate the structured data has at least some fields filled"""
        try:
            # Check if personal info has at least some data
            personal_info_valid = any(data["personal_info"].values())
            
            # Check if any of the arrays have entries
            arrays_valid = (
                len(data["education"]) > 0 or
                len(data["experience"]) > 0 or
                len(data["skills"]["technical"]) > 0 or
                len(data["skills"]["soft"]) > 0 or
                len(data["projects"]) > 0
            )
            
            return personal_info_valid or arrays_valid
            
        except Exception:
            return False