# agents/parser_agent.py

from typing import Dict, Any
import json
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from models.data_models import JobDescription, ResumeData

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
            Parse the following markdown content and extract structured information about the job description and resume.
            Include all important details like responsibilities, qualifications, skills, and experience.
            
            Content:
            {content}
            
            Return the parsed information in a JSON format with two main sections:
            1. job_description
            2. resume_data
            
            Make sure the JSON is properly formatted and contains all the information from the markdown.
            """
        )
        
    def parse_markdown(self, markdown_content: str) -> Dict[str, Any]:
        """Parse markdown content into structured data"""
        try:
            # Get structured data from LLM
            result = (self.parse_prompt | self.llm).invoke({"content": markdown_content})
            
            # Extract the generated text
            parsed_data_str = result.content 
            
            # --- DEBUG: Print raw LLM output --- 
            print("--- Raw LLM Output for Parsing ---")
            print(parsed_data_str)
            print("--- End Raw LLM Output ---")
            # --- END DEBUG --- 
            
            # Strip potential markdown fences
            if parsed_data_str.startswith("```json"):
                parsed_data_str = parsed_data_str[len("```json"):].strip()
            if parsed_data_str.endswith("```"):
                parsed_data_str = parsed_data_str[:-len("```")].strip()
            
            # Need to parse the JSON string now
            parsed_data = json.loads(parsed_data_str)
            
            # Convert to Pydantic models
            job_description = JobDescription(**parsed_data["job_description"])
            resume_data = ResumeData(**parsed_data["resume_data"])
            
            return {
                "job_description": job_description,
                "resume_data": resume_data
            }
            
        except Exception as e:
            print(f"Error parsing markdown: {str(e)}")
            raise
        
    def extract_key_matches(self, parsed_data: Dict[str, Any]) -> Dict[str, list]:
        """Extract matching elements between JD and resume"""
        jd = parsed_data["job_description"]
        resume = parsed_data["resume_data"]
        
        matches = {
            "skills": [
                skill for skill in resume.skills 
                if skill.lower() in [q.lower() for q in jd.qualifications]
            ],
            "experience": [],
            "education": []
        }
        
        # Match experience
        for exp in resume.experience:
            for resp in jd.responsibilities:
                if any(keyword.lower() in exp["description"].lower() 
                      for keyword in resp.split()):
                    matches["experience"].append(exp)
                    break
                    
        return matches

    def get_candidate_level(self, parsed_data: Dict[str, Any]) -> str:
        """Determine candidate experience level"""
        resume = parsed_data["resume_data"]
        total_experience = sum(
            float(exp.get("duration", "0").split()[0]) 
            for exp in resume.experience 
            if "duration" in exp
        )
        
        if total_experience < 2:
            return "junior"
        elif total_experience < 5:
            return "mid"
        else:
            return "senior"