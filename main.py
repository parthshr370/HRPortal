# main.py
import logging
import argparse
import json
from pathlib import Path
from uuid import uuid4
import sys

# Import configuration
from config.config import (
    BASE_DIR, DATA_DIR, SAMPLE_DIR, OUTPUT_DIR,
    RESUME_DIR, JD_DIR, TEMPLATE_DIR, 
    LLM_CONFIG, NON_REASONING_LLM_CONFIG
)
from config.logging_config import setup_logging

# Import models
from models.candidate import CandidateProfile, NormalizedCandidate
from models.question import Question, QuestionTemplate, ReferenceAnswer
from models.assessment import Assessment, CandidateResponse
from models.evaluation import QuestionEvaluation, AssessmentEvaluation

# Import services
from services.data_integration import DataIntegrationService
from services.profile_analyzer import ProfileAnalyzerService
from services.question_generator import QuestionGeneratorService
from services.answer_generator import AnswerGeneratorService
from services.evaluator import EvaluatorService

# Import utilities
from utils.persistence import FilePersistence, create_sample_data
from utils.llm_utils import LLMService
from utils.validation import load_and_validate_json

# Setup logging
loggers = setup_logging()
logger = loggers["main"]

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="OA Generation Agent Pipeline")
    parser.add_argument("--resume", type=str, help="Path to resume JSON file")
    parser.add_argument("--jd", type=str, help="Path to job description JSON file")
    parser.add_argument("--create-sample", action="store_true", help="Create sample data files")
    parser.add_argument("--num-questions", type=int, default=5, help="Number of questions to generate")
    parser.add_argument("--evaluate", action="store_true", help="Evaluate a candidate's responses")
    parser.add_argument("--assessment-id", type=str, help="Assessment ID to evaluate")
    parser.add_argument("--responses", type=str, help="Path to candidate responses JSON file")
    return parser.parse_args()


def initialize_services():
    """Initialize all services."""
    logger.info("Initializing services")
    
    # Initialize services with appropriate LLM configurations
    data_integration_service = DataIntegrationService()
    
    # Non-reasoning tasks
    profile_analyzer_service = ProfileAnalyzerService(NON_REASONING_LLM_CONFIG)
    question_generator_service = QuestionGeneratorService(TEMPLATE_DIR, NON_REASONING_LLM_CONFIG)
    
    # Reasoning tasks
    answer_generator_service = AnswerGeneratorService(LLM_CONFIG)
    evaluator_service = EvaluatorService(LLM_CONFIG)
    
    # Initialize LLM services for testing
    reasoning_llm_service = LLMService(LLM_CONFIG)
    non_reasoning_llm_service = LLMService(NON_REASONING_LLM_CONFIG)
    
    logger.info("Services initialized")
    
    return {
        "data_integration": data_integration_service,
        "profile_analyzer": profile_analyzer_service,
        "question_generator": question_generator_service,
        "answer_generator": answer_generator_service,
        "evaluator": evaluator_service,
        "reasoning_llm": reasoning_llm_service,
        "non_reasoning_llm": non_reasoning_llm_service
    }

def initialize_persistence():
    """Initialize persistence layers."""
    logger.info("Initializing persistence layers")
    
    # Initialize persistence layers
    candidate_persistence = FilePersistence(OUTPUT_DIR, NormalizedCandidate, "candidates")
    assessment_persistence = FilePersistence(OUTPUT_DIR, Assessment, "assessments")
    response_persistence = FilePersistence(OUTPUT_DIR, CandidateResponse, "responses")
    evaluation_persistence = FilePersistence(OUTPUT_DIR, AssessmentEvaluation, "evaluations")
    
    logger.info("Persistence layers initialized")
    
    return {
        "candidate": candidate_persistence,
        "assessment": assessment_persistence,
        "response": response_persistence,
        "evaluation": evaluation_persistence
    }

def configure_pipeline():
    """Configure the pipeline with OpenRouter keys."""
    import os
    from dotenv import load_dotenv, set_key
    
    logger.info("Configuring the pipeline with OpenRouter keys")
    
    # Ask for OpenRouter keys
    reasoning_key = input("Enter your OpenRouter REASONING API key: ")
    non_reasoning_key = input("Enter your OpenRouter NON-REASONING API key: ")
    
    # Ask for model names
    reasoning_model = input("Enter your OpenRouter REASONING model [default: openai/o3e-mini]: ") or "openai/o3e-mini"
    non_reasoning_model = input("Enter your OpenRouter NON-REASONING model [default: gemini-flash-2.0]: ") or "gemini-flash-2.0"
    
    # Update .env file
    env_path = Path(BASE_DIR) / '.env'
    
    # Load existing .env file
    load_dotenv(env_path)
    
    # Set the keys
    set_key(env_path, "OPENROUTER_REASONING_API_KEY", reasoning_key)
    set_key(env_path, "OPENROUTER_NON_REASONING_API_KEY", non_reasoning_key)
    set_key(env_path, "LLM_PROVIDER", "openrouter")
    set_key(env_path, "REASONING_MODEL", reasoning_model)
    set_key(env_path, "NON_REASONING_MODEL", non_reasoning_model)
    
    logger.info("Pipeline configured successfully!")
    logger.info(f"Using {non_reasoning_model} for non-reasoning tasks (profile analysis, question generation)")
    logger.info(f"Using {reasoning_model} for reasoning tasks (answer generation, evaluation)")
    
    return True

def generate_assessment(services, persistence, resume_path, jd_path, num_questions):
    """Generate an assessment for a candidate."""
    logger.info("Generating assessment")
    
    # Load and validate resume
    resume_data, error = load_and_validate_json(Path(resume_path), "resume")
    if error:
        logger.error(f"Error loading resume: {error}")
        return None
    
    # Load and validate job description
    jd_data, error = load_and_validate_json(Path(jd_path), "job_description")
    if error:
        logger.error(f"Error loading job description: {error}")
        return None
    
    # 1. Data Integration
    logger.info("Step 1: Data Integration")
    candidate_profile = services["data_integration"].normalize_resume(resume_data)
    if not candidate_profile:
        logger.error("Failed to normalize resume")
        return None
    
    # 2. Profile Analysis
    logger.info("Step 2: Profile Analysis")
    normalized_candidate = services["profile_analyzer"].analyze_profile(candidate_profile)
    persistence["candidate"].save(normalized_candidate)
    
    # Generate a candidate ID
    candidate_id = str(uuid4())
    job_id = str(uuid4())
    
    # 3. Question Generation
    logger.info("Step 3: Question Generation")
    questions = services["question_generator"].generate_questions(
        normalized_candidate, jd_data, num_questions
    )
    
    # 4. Answer Generation
    logger.info("Step 4: Answer Generation")
    reference_answers = services["answer_generator"].generate_reference_answers(questions)
    
    # Create a reference answer map for easier lookup
    reference_answer_map = {answer.question_id: answer for answer in reference_answers}
    
    # 5. Create Assessment
    assessment = Assessment(
        assessment_id=str(uuid4()),
        candidate_id=candidate_id,
        job_id=job_id,
        questions=questions,
        reference_answers=reference_answers,
        metadata={
            "candidate_name": candidate_profile.name,
            "job_title": jd_data.get("title", "Unknown"),
            "company": jd_data.get("company", "Unknown")
        }
    )
    
    # Save assessment
    persistence["assessment"].save(assessment)
    
    logger.info(f"Assessment generated with ID: {assessment.assessment_id}")
    logger.info(f"Generated {len(questions)} questions and {len(reference_answers)} reference answers")
    
    # Print assessment details
    print("\n" + "="*50)
    print(f"Assessment generated for {candidate_profile.name}")
    print(f"Job: {jd_data.get('title', 'Unknown')} at {jd_data.get('company', 'Unknown')}")
    print(f"Assessment ID: {assessment.assessment_id}")
    print(f"Number of questions: {len(questions)}")
    print("="*50 + "\n")
    
    # Print questions
    print("Generated Questions:")
    for i, question in enumerate(questions):
        print(f"\nQuestion {i+1} ({question.difficulty} {question.question_type}):")
        print(f"Category: {question.category} - {question.subcategory}")
        print(f"Content: {question.content}\n")
        print(f"Skills tested: {', '.join(question.skills_tested)}")
        print("-"*50)
    
    return assessment

def evaluate_assessment(services, persistence, assessment_id, responses_path):
    """Evaluate a candidate's responses to an assessment."""
    logger.info(f"Evaluating assessment: {assessment_id}")
    
    # Load assessment
    assessment = persistence["assessment"].load(assessment_id)
    if not assessment:
        logger.error(f"Assessment not found: {assessment_id}")
        return None
    
    # Load and validate responses
    responses_data, error = load_and_validate_json(Path(responses_path), "responses")
    if error:
        logger.error(f"Error loading responses: {error}")
        return None
    
    # Parse candidate responses
    candidate_responses = []
    for response_data in responses_data:
        candidate_response = CandidateResponse(
            response_id=response_data.get("response_id", str(uuid4())),
            assessment_id=assessment_id,
            question_id=response_data.get("question_id"),
            response_text=response_data.get("response_text"),
            metadata=response_data.get("metadata", {})
        )
        candidate_responses.append(candidate_response)
        
        # Save individual response
        persistence["response"].save(candidate_response)
    
    # Create a response map for easier lookup
    response_map = {response.question_id: response for response in candidate_responses}
    
    # Create a question map for easier lookup
    question_map = {question.question_id: question for question in assessment.questions}
    
    # Create a reference answer map for easier lookup
    reference_answer_map = {answer.question_id: answer for answer in assessment.reference_answers}
    
    # Evaluate responses
    question_evaluations = []
    for question_id, response in response_map.items():
        # Get corresponding question and reference answer
        question = question_map.get(question_id)
        reference_answer = reference_answer_map.get(question_id)
        
        if not question or not reference_answer:
            logger.warning(f"Question or reference answer not found for response: {question_id}")
            continue
        
        # Evaluate response
        evaluation = services["evaluator"].evaluate_response(
            question, reference_answer, response
        )
        
        question_evaluations.append(evaluation)
    
    # Create assessment evaluation
    assessment_evaluation = AssessmentEvaluation(
        evaluation_id=str(uuid4()),
        assessment_id=assessment_id,
        candidate_id=assessment.candidate_id,
        question_evaluations=question_evaluations,
        overall_score=services["evaluator"].calculate_overall_score(question_evaluations),
        feedback=services["evaluator"].generate_overall_feedback(question_evaluations)
    )
    
    # Save assessment evaluation
    persistence["evaluation"].save(assessment_evaluation)
    
    logger.info(f"Assessment evaluation generated with ID: {assessment_evaluation.evaluation_id}")
    
    return assessment_evaluation

def main():
    """Main entry point for the OA Generation Agent Pipeline."""
    args = parse_args()
    
    # Create sample data if requested
    if args.create_sample:
        create_sample_data(SAMPLE_DIR)
        return
    
    # Initialize services and persistence
    services = initialize_services()
    persistence = initialize_persistence()
    
    # Test LLM configuration if needed
    test_reasoning = services["reasoning_llm"].generate_text("Hello, I'm testing the reasoning LLM configuration.")
    test_non_reasoning = services["non_reasoning_llm"].generate_text("Hello, I'm testing the non-reasoning LLM configuration.")
    
    logger.info("LLM test results:")
    if test_reasoning is not None:
        logger.info(f"Reasoning LLM: {test_reasoning[:100]}...")
    else:
        logger.info("Reasoning LLM: No response received (API call may have failed)")

    if test_non_reasoning is not None:
        logger.info(f"Non-reasoning LLM: {test_non_reasoning[:100]}...")
    else:
        logger.info("Non-reasoning LLM: No response received (API call may have failed)")
    
    # Evaluate an assessment if requested
    if args.evaluate:
        if not args.assessment_id or not args.responses:
            logger.error("Assessment ID and responses path are required for evaluation")
            return
        
        evaluation = evaluate_assessment(
            services, persistence, args.assessment_id, args.responses
        )
        
        if evaluation:
            # Print evaluation summary
            print("\nEvaluation Summary:")
            print(f"Assessment ID: {evaluation.assessment_id}")
            print(f"Overall Score: {evaluation.overall_score}")
            print(f"Feedback: {evaluation.feedback}")
            print("\nQuestion Evaluations:")
            for qe in evaluation.question_evaluations:
                print(f"Question ID: {qe.question_id}, Score: {qe.score}, Correctness: {qe.correctness if hasattr(qe, 'correctness') else 'N/A'}")
                print(f"Feedback: {qe.feedback}")
                print()
        
        return
    
    # Generate an assessment if resume and job description are provided
    if args.resume and args.jd:
        assessment = generate_assessment(
            services, persistence, args.resume, args.jd, args.num_questions
        )
        
        if assessment:
            # Print assessment summary
            print("\nAssessment Summary:")
            print(f"Assessment ID: {assessment.assessment_id}")
            print(f"Candidate: {assessment.metadata.get('candidate_name')}")
            print(f"Job: {assessment.metadata.get('job_title')} at {assessment.metadata.get('company')}")
            print(f"Number of Questions: {len(assessment.questions)}")
            print("\nQuestions:")
            for i, question in enumerate(assessment.questions, 1):
                print(f"{i}. {question.content}")  # Fixed: using content instead of question_text
                print(f"   Type: {question.question_type}, Difficulty: {question.difficulty}")
                print()
        
        return
    
    # Print help if no action is specified
    print("No action specified. Use --help for more information.")

if __name__ == "__main__":
    main()