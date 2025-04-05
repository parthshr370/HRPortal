# agents/parser_agent.py

from typing import Dict, Any
import json
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from models.data_models import JobDescription, ResumeData
from utils.md_parser import MarkdownParser

class ParserAgent:
    """Agent for parsing markdown input containing JD and resume"""
    
    def __init__(self, non_reasoning_api_key: str):
        """Initialize parser agent with API key"""
        self.llm = ChatOpenAI(
            model="google/gemini-flash-1.5",
            temperature=0.2,
            openai_api_key=non_reasoning_api_key,
            openai_api_base="https://openrouter.ai/api/v1",
            max_tokens=4096
        )
        
        self.parse_prompt = PromptTemplate(
            input_variables=["content"],
            template="""
            You are a specialized parser that extracts structured information from text containing job descriptions and resumes.
            Analyze the following raw text content:

            {content}
            
            Extract all important details. First identify which parts are the job description and which parts are the resume.
            Then extract details such as job title, responsibilities, qualifications, candidate's name, education, experience, skills, etc.
            
            Return the information in a JSON format with exactly these two main sections:
            1. job_description - Include job_title (string), location (string), experience_level (string), 
               responsibilities (array of strings), qualifications (array of strings), and preferred_qualifications (array of strings)
            2. resume_data - Include personal_info (object with name), education (array), experience (array), 
               skills (array of strings), projects (array), certifications (array)
            
            Use default values for any missing fields. Every field must be included.

            For example:
            {{
                "job_description": {{
                    "job_title": "Software Engineer",
                    "location": "New York",
                    "experience_level": "Mid-level",
                    "responsibilities": ["Develop software", "Test code"],
                    "qualifications": ["Python", "JavaScript"],
                    "preferred_qualifications": ["React", "AWS"]
                }},
                "resume_data": {{
                    "personal_info": {{ "name": "John Doe" }},
                    "education": [{{ "degree": "BS Computer Science", "institution": "Example University" }}],
                    "experience": [{{ "title": "Developer", "company": "Tech Co", "duration": "2 years" }}],
                    "skills": ["Python", "Java"],
                    "projects": [],
                    "certifications": []
                }}
            }}
            """
        )
        
        self.match_prompt = PromptTemplate(
            input_variables=["job_description", "resume_data"],
            template="""
            Analyze the job description and resume data to find matches:
            
            JOB DESCRIPTION:
            {job_description}
            
            RESUME:
            {resume_data}
            
            Find all skills, experience, and education in the resume that match requirements in the job description.
            
            Return a JSON object with the following structure:
            {{
                "skills": ["matching skill 1", "matching skill 2"],
                "experience": [{{...matching experience objects...}}],
                "education": [{{...matching education objects...}}]
            }}
            """
        )
        
        self.level_prompt = PromptTemplate(
            input_variables=["resume_data"],
            template="""
            Based on this resume data:
            
            {resume_data}
            
            Determine the candidate's experience level.
            Consider years of experience, job titles, and responsibilities.
            
            Return ONLY ONE of these exact values: "junior", "mid", or "senior"
            """
        )
    
    def parse_markdown(self, markdown_content: str) -> Dict[str, Any]:
        """Parse markdown content into structured data"""
        try:
            # Step 1: Extract raw text (super simple preprocessing)
            raw_text = MarkdownParser.extract_raw_text(markdown_content)
            
            # Step 2: Let the LLM handle all the parsing
            result = self.llm.invoke(self.parse_prompt.format(content=raw_text))
            parsed_text = result.content
            
            # Clean up potential markdown code blocks
            if "```json" in parsed_text:
                parsed_text = parsed_text.split("```json", 1)[1]
            if "```" in parsed_text:
                parsed_text = parsed_text.split("```", 1)[0]
            
            # Parse JSON with default values
            try:
                data = json.loads(parsed_text.strip())
                
                # Ensure the correct structure
                if "job_description" not in data:
                    data["job_description"] = {
                        "job_title": "Software Engineer",
                        "location": "Remote",
                        "experience_level": "Mid-level",
                        "responsibilities": ["Development"],
                        "qualifications": ["Programming"],
                        "preferred_qualifications": []
                    }
                
                if "resume_data" not in data:
                    data["resume_data"] = {
                        "personal_info": {"name": "Candidate"},
                        "education": [],
                        "experience": [],
                        "skills": ["Programming"],
                        "projects": [],
                        "certifications": []
                    }
                
                # Create Pydantic models
                job_description = JobDescription(
                    job_title=data["job_description"].get("job_title", "Software Engineer"),
                    location=data["job_description"].get("location", "Remote"),
                    experience_level=data["job_description"].get("experience_level", "Mid-level"),
                    responsibilities=data["job_description"].get("responsibilities", ["Development"]),
                    qualifications=data["job_description"].get("qualifications", ["Programming"]),
                    preferred_qualifications=data["job_description"].get("preferred_qualifications", [])
                )
                
                resume_data = ResumeData(
                    personal_info=data["resume_data"].get("personal_info", {"name": "Candidate"}),
                    summary=data["resume_data"].get("summary", ""),
                    education=data["resume_data"].get("education", []),
                    experience=data["resume_data"].get("experience", []),
                    skills=data["resume_data"].get("skills", ["Programming"]),
                    projects=data["resume_data"].get("projects", []),
                    certifications=data["resume_data"].get("certifications", [])
                )
                
                return {
                    "job_description": job_description,
                    "resume_data": resume_data
                }
                
            except json.JSONDecodeError as e:
                print(f"JSON parsing error: {e}")
                print(f"Raw text received: {parsed_text}")
                # Fall back to default values
                
        except Exception as e:
            print(f"Error in parse_markdown: {e}")
        
        # Return default values if anything goes wrong
        return {
            "job_description": JobDescription(
                job_title="Software Engineer",
                location="Remote",
                experience_level="Mid-level",
                responsibilities=["Development"],
                qualifications=["Programming"],
                preferred_qualifications=[]
            ),
            "resume_data": ResumeData(
                personal_info={"name": "Candidate"},
                summary="",
                education=[],
                experience=[],
                skills=["Programming"],
                projects=[],
                certifications=[]
            )
        }
        
    def extract_key_matches(self, parsed_data: Dict[str, Any]) -> Dict[str, list]:
        """Extract matching elements between JD and resume"""
        try:
            # Let the LLM find matches
            result = self.llm.invoke(self.match_prompt.format(
                job_description=json.dumps(parsed_data["job_description"].dict()),
                resume_data=json.dumps(parsed_data["resume_data"].dict())
            ))
            
            matches_text = result.content
            
            # Clean up potential markdown code blocks
            if "```json" in matches_text:
                matches_text = matches_text.split("```json", 1)[1]
            if "```" in matches_text:
                matches_text = matches_text.split("```", 1)[0]
            
            matches = json.loads(matches_text.strip())
            
            # Ensure we have the expected structure
            if "skills" not in matches:
                matches["skills"] = []
            if "experience" not in matches:
                matches["experience"] = []
            if "education" not in matches:
                matches["education"] = []
                
            return matches
            
        except Exception as e:
            print(f"Error in extract_key_matches: {e}")
            
            # Create a basic fallback
            return {
                "skills": parsed_data["resume_data"].skills[:2],
                "experience": parsed_data["resume_data"].experience[:1],
                "education": []
            }

    def get_candidate_level(self, parsed_data: Dict[str, Any]) -> str:
        """Determine candidate experience level"""
        try:
            # Let the LLM determine the level
            result = self.llm.invoke(self.level_prompt.format(
                resume_data=json.dumps(parsed_data["resume_data"].dict())
            ))
            
            level = result.content.strip().lower()
            
            # Validate the result
            if level in ["junior", "mid", "senior"]:
                return level
            else:
                return "mid"  # Default
                
        except Exception as e:
            print(f"Error in get_candidate_level: {e}")
            return "mid"  # Default fallback