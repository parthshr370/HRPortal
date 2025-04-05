# main.py

import os
import json
from dotenv import load_dotenv
from typing import Dict, Any, Optional
import asyncio
from agents.parser_agent import ParserAgent
from agents.question_generator import QuestionGenerator
from agents.assessment_agent import AssessmentAgent
from models.data_models import Assessment, AssessmentResult

class OAModule:
    """Main class for Online Assessment Module"""
    
    def __init__(self):
        """Initialize OA Module with necessary agents"""
        load_dotenv()
        
        self.non_reasoning_key = os.getenv("NON_REASONING_API_KEY")
        self.reasoning_key = os.getenv("REASONING_API_KEY")
        
        if not self.non_reasoning_key or not self.reasoning_key:
            raise ValueError("API keys not found in environment variables")
            
        # Initialize agents
        self.parser = ParserAgent(self.non_reasoning_key)
        self.generator = QuestionGenerator(self.non_reasoning_key)
        self.assessor = AssessmentAgent(self.reasoning_key)
        
    async def process_input(self, markdown_content: str) -> Assessment:
        """Process markdown input and generate assessment"""
        try:
            # Parse input content
            parsed_data = self.parser.parse_markdown(markdown_content)
            
            # Extract key information
            job_desc = parsed_data["job_description"]
            resume = parsed_data["resume_data"]
            matches = self.parser.extract_key_matches(parsed_data)
            level = self.parser.get_candidate_level(parsed_data)
            
            # Generate assessment
            assessment = await self.generator.generate_assessment(
                candidate_name=resume.personal_info["name"],
                job_title=job_desc.title,
                skills=matches["skills"],
                experience=matches["experience"],
                level=level,
                resume_data=resume.dict(),
                job_desc=job_desc.dict()
            )
            
            return assessment
            
        except Exception as e:
            print(f"Error processing input: {str(e)}")
            raise
        
    async def evaluate_responses(
        self,
        assessment: Assessment,
        responses: Dict[str, str]
    ) -> AssessmentResult:
        """Evaluate candidate responses"""
        try:
            result = await self.assessor.evaluate_assessment(assessment, responses)
            return result
        except Exception as e:
            print(f"Error evaluating responses: {str(e)}")
            raise
        
    def generate_report(self, result: AssessmentResult) -> str:
        """Generate human-readable report"""
        try:
            return self.assessor.generate_summary_report(result)
        except Exception as e:
            print(f"Error generating report: {str(e)}")
            raise

async def main(markdown_file: str, response_file: Optional[str] = None):
    """Main function to run the OA module"""
    try:
        # Initialize module
        oa_module = OAModule()
        
        # Read input markdown
        with open(markdown_file, 'r') as f:
            markdown_content = f.read()
            
        # Generate assessment
        assessment = await oa_module.process_input(markdown_content)
        print(f"Generated assessment with {len(assessment.coding_questions)} coding questions, "
              f"{len(assessment.system_design_questions)} system design questions, and "
              f"{len(assessment.behavioral_questions)} behavioral questions.")
        
        # If response file provided, evaluate responses
        if response_file:
            with open(response_file, 'r') as f:
                responses = json.load(f)
                
            result = await oa_module.evaluate_responses(assessment, responses)
            report = oa_module.generate_report(result)
            print("\nAssessment Report:")
            print(report)
            
        return assessment
        
    except Exception as e:
        print(f"Error running OA module: {str(e)}")
        raise

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run Online Assessment Module")
    parser.add_argument("markdown_file", help="Path to input markdown file")
    parser.add_argument("--responses", help="Path to JSON file with responses")
    
    args = parser.parse_args()
    
    asyncio.run(main(args.markdown_file, args.responses))