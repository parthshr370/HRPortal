import argparse
import json
import os
from config.config import MODELS
from utils.file_handlers import FileHandler
from utils.text_preprocessing import TextPreprocessor
from agents.resume_parsing_agent import ResumeParsingAgent
from agents.job_matching_agent import JobMatchingAgent
from agents.decision_feedback_agent import DecisionFeedbackAgent

def ensure_output_directory(output_path: str):
    """Ensure the output directory exists"""
    if output_path:
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)

def process_resume(resume_path: str, job_description_path: str = None, output_path: str = None):
    try:
        # Ensure output directory exists if output path is provided
        ensure_output_directory(output_path)
        
        # Initialize components
        file_handler = FileHandler()
        text_preprocessor = TextPreprocessor()
        
        # Extract and clean resume text
        print("Processing resume...")
        resume_text = file_handler.extract_text(resume_path)
        print(f"\nExtracted text length: {len(resume_text)}")
        print("\nFirst 500 characters of extracted text:")
        print(resume_text[:500])
        
        cleaned_resume_text = text_preprocessor.clean_text(resume_text)
        print("\nCleaned text length:", len(cleaned_resume_text))
        print("\nFirst 500 characters of cleaned text:")
        print(cleaned_resume_text[:500])
        
        # Initialize resume parsing agent
        print("\nInitializing resume parsing agent...")
        resume_parser = ResumeParsingAgent(
            api_key=MODELS['non_reasoning']['api_key'],
            model_name=MODELS['non_reasoning']['name']
        )
        
        # Parse resume
        print("\nParsing resume...")
        parsed_resume = resume_parser.parse_resume(cleaned_resume_text)
        
        # Save parsed resume if output path provided
        if output_path:
            output_file = f"{output_path}_parsed_resume.json"
            print(f"\nSaving parsed resume to: {output_file}")
            with open(output_file, 'w') as f:
                json.dump(parsed_resume, f, indent=2)
        
        # Print parsed resume
        print("\nParsed Resume:")
        print(json.dumps(parsed_resume, indent=2))
        
        # Process job description if provided
        if job_description_path:
            process_job_matching(
                job_description_path,
                parsed_resume,
                file_handler,
                text_preprocessor,
                output_path
            )
            
    except Exception as e:
        print(f"Error: {str(e)}")
        print("\nDebug information:")
        import traceback
        traceback.print_exc()

def process_job_matching(job_description_path, parsed_resume, file_handler, text_preprocessor, output_path):
    try:
        # Read and clean job description
        print("\nProcessing job description...")
        job_desc_text = file_handler.extract_text(job_description_path)
        cleaned_job_desc = text_preprocessor.clean_text(job_desc_text)
        
        # Initialize job matching agent
        job_matcher = JobMatchingAgent(
            api_key=MODELS['reasoning']['api_key'],
            model_name=MODELS['reasoning']['name']
        )
        
        # Perform job matching
        print("Analyzing job match...")
        match_analysis = job_matcher.match_job(parsed_resume, cleaned_job_desc)
        
        # Save match analysis if output path provided
        if output_path:
            output_file = f"{output_path}_match_analysis.json"
            print(f"\nSaving match analysis to: {output_file}")
            with open(output_file, 'w') as f:
                json.dump(match_analysis, f, indent=2)
        
        print("\nJob Match Analysis:")
        print(json.dumps(match_analysis, indent=2))
        
        # Generate decision feedback
        process_decision_feedback(parsed_resume, match_analysis, cleaned_job_desc, output_path)
        
    except Exception as e:
        print(f"Error in job matching: {str(e)}")
        raise

def process_decision_feedback(parsed_resume, match_analysis, job_desc, output_path):
    try:
        decision_agent = DecisionFeedbackAgent(
            api_key=MODELS['reasoning']['api_key'],
            model_name=MODELS['reasoning']['name']
        )
        
        print("\nGenerating hiring decision...")
        decision = decision_agent.generate_decision(
            candidate_profile=parsed_resume,
            match_analysis=match_analysis,
            job_requirements=job_desc
        )
        
        # Save decision if output path provided
        if output_path:
            output_file = f"{output_path}_decision.json"
            print(f"\nSaving decision to: {output_file}")
            with open(output_file, 'w') as f:
                json.dump(decision, f, indent=2)
        
        print_decision_summary(decision)
        
    except Exception as e:
        print(f"Error in decision feedback: {str(e)}")
        raise

def print_decision_summary(decision):
    print("\nHiring Decision Summary:")
    print(f"Status: {decision['decision']['status']}")
    print(f"Confidence Score: {decision['decision']['confidence_score']}%")
    print(f"Recommended Interview Stage: {decision['decision']['interview_stage']}")
    
    print("\nKey Strengths:")
    for strength in decision['rationale']['key_strengths']:
        print(f"- {strength}")
    
    print("\nAreas of Concern:")
    for concern in decision['rationale']['concerns']:
        print(f"- {concern}")
    
    print("\nNext Steps:")
    for action in decision['next_steps']['immediate_actions']:
        print(f"- {action}")

def main():
    parser = argparse.ArgumentParser(description='ATS Resume Parser and Job Matcher')
    parser.add_argument('resume', help='Path to the resume file')
    parser.add_argument('--job', '-j', help='Path to the job description file')
    parser.add_argument('--output', '-o', help='Base path for output files')
    
    args = parser.parse_args()
    
    process_resume(args.resume, args.job, args.output)

if __name__ == "__main__":
    main()