# services/evaluator.py
import logging
from typing import Dict, List, Any, Optional, Tuple
import json
from uuid import uuid4

from langchain_community.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

from models.question import Question, ReferenceAnswer, QuestionType
from models.assessment import CandidateResponse
from models.evaluation import QuestionEvaluation, AssessmentEvaluation
from config.config import LLM_CONFIG  # Default is reasoning configuration

logger = logging.getLogger("evaluator")

class EvaluatorService:
    """Service to evaluate candidate responses against reference answers."""
    
    def __init__(self, llm_config: Dict[str, Any] = None):
        """Initialize the service with LLM configuration."""
        logger.info("Initializing Evaluator Service")
        
        # Use reasoning configuration by default
        self.llm_config = llm_config if llm_config else LLM_CONFIG
        
        logger.info(f"Using {self.llm_config.get('provider')} for evaluation with model {self.llm_config.get('model_name')}")
        
        # Define evaluation prompts for different question types
        self.evaluation_prompts = {
            QuestionType.MULTIPLE_CHOICE: """
            Evaluate this candidate's answer to a multiple choice question.
            
            Question: {question}
            Reference Answer: {reference_answer}
            Candidate's Answer: {candidate_answer}
            
            Key points that should be present:
            {key_points}
            
            Evaluate the answer on:
            1. Correctness of selected option (70%)
            2. Quality of explanation (30%)
            
            Provide a score from 0-100 and detailed feedback.
            """,
            
            QuestionType.CODING: """
            Evaluate this candidate's coding solution.
            
            Question: {question}
            Reference Solution: {reference_answer}
            Candidate's Solution: {candidate_answer}
            
            Key points to evaluate:
            {key_points}
            
            Scoring rubric:
            {scoring_rubric}
            
            Evaluate the solution on:
            1. Correctness - Does it solve the problem? (40%)
            2. Efficiency - Is it an optimal solution? (30%)
            3. Code quality - Is it well-structured and readable? (20%)
            4. Error handling - Does it handle edge cases? (10%)
            
            Provide a score from 0-100 and detailed feedback.
            """,
            
            QuestionType.SHORT_ANSWER: """
            Evaluate this candidate's short answer response.
            
            Question: {question}
            Reference Answer: {reference_answer}
            Candidate's Answer: {candidate_answer}
            
            Key points that should be present:
            {key_points}
            
            Scoring rubric:
            {scoring_rubric}
            
            Provide a score from 0-100 and detailed feedback.
            """,
            
            QuestionType.OPEN_ENDED: """
            Evaluate this candidate's open-ended response.
            
            Question: {question}
            Reference Answer: {reference_answer}
            Candidate's Answer: {candidate_answer}
            
            Key points that should be addressed:
            {key_points}
            
            Scoring rubric:
            {scoring_rubric}
            
            Evaluate on:
            1. Comprehensiveness - Covers all important aspects (30%)
            2. Accuracy - Information is correct (30%)
            3. Reasoning - Logic is sound (30%)
            4. Communication - Clear and well-structured (10%)
            
            Provide a score from 0-100 and detailed feedback.
            """
        }
    
    def evaluate_response(self, question: Question, reference_answer: ReferenceAnswer, 
                          candidate_response: CandidateResponse) -> QuestionEvaluation:
        """Evaluate a candidate's response to a question against the reference answer."""
        logger.info(f"Evaluating response {candidate_response.response_id} for question {question.question_id}")
        
        # In a production environment, we would use the LLM to evaluate the response
        # Here's how it would be structured:
        
        """
        # Get the appropriate evaluation prompt
        prompt_template = self.evaluation_prompts.get(question.question_type)
        if not prompt_template:
            logger.error(f"No evaluation prompt found for question type {question.question_type}")
            # Return a default evaluation with low confidence
            return self._create_default_evaluation(candidate_response, 0, "Unable to evaluate question type")
        
        # Create prompt
        prompt = PromptTemplate(
            template=prompt_template,
            input_variables=["question", "reference_answer", "candidate_answer", "key_points", "scoring_rubric"]
        )
        
        # Initialize LLM
        llm = ChatOpenAI(
            model_name=self.llm_config.get("model_name", "gpt-4"),
            temperature=0.1  # Lower temperature for more consistent evaluation
        )
        
        # Create chain
        chain = LLMChain(llm=llm, prompt=prompt)
        
        # Generate evaluation
        result = chain.run(
            question=question.content,
            reference_answer=reference_answer.content,
            candidate_answer=candidate_response.content,
            key_points="\n".join([f"- {point}" for point in reference_answer.key_points]),
            scoring_rubric="\n".join([f"- {k}: {v}" for k, v in reference_answer.scoring_rubric.items()])
        )
        
        # Parse result to extract score and feedback
        # In a real implementation, we would structure the LLM output and parse it
        score, feedback = self._parse_evaluation_result(result)
        """
        
        # For now, we'll create a mock evaluation
        score, feedback, key_points_matched = self._mock_evaluate_response(
            question, reference_answer, candidate_response
        )
        
        # Create evaluation
        evaluation = QuestionEvaluation(
            evaluation_id=str(uuid4()),
            response_id=candidate_response.response_id,
            question_id=question.question_id,
            score=score,
            feedback=feedback,
            confidence=0.85,  # Mock confidence level
            key_points_matched=key_points_matched
        )
        
        logger.info(f"Evaluation complete for response {candidate_response.response_id}: score={score}")
        return evaluation
    
    def evaluate_assessment(self, questions: List[Question], 
                           reference_answers: Dict[str, ReferenceAnswer],
                           candidate_responses: Dict[str, CandidateResponse],
                           assessment_id: str, candidate_id: str) -> AssessmentEvaluation:
        """Evaluate a complete assessment."""
        logger.info(f"Evaluating assessment {assessment_id} for candidate {candidate_id}")
        
        question_evaluations = []
        total_score = 0
        question_count = 0
        
        # Track strengths and areas for improvement
        strengths = []
        areas_for_improvement = []
        
        # Evaluate each question
        for question in questions:
            # Skip if no reference answer or candidate response
            if question.question_id not in reference_answers or question.question_id not in candidate_responses:
                logger.warning(f"Missing reference answer or candidate response for question {question.question_id}")
                continue
            
            reference_answer = reference_answers[question.question_id]
            candidate_response = candidate_responses[question.question_id]
            
            # Evaluate response
            evaluation = self.evaluate_response(question, reference_answer, candidate_response)
            question_evaluations.append(evaluation)
            
            # Update total score
            total_score += evaluation.score
            question_count += 1
            
            # Identify strengths and areas for improvement
            if evaluation.score >= 80:
                strengths.append(f"Strong understanding of {question.subcategory}")
            elif evaluation.score <= 50:
                areas_for_improvement.append(f"Needs improvement in {question.subcategory}")
        
        # Calculate overall score
        overall_score = total_score / question_count if question_count > 0 else 0
        
        # Create assessment evaluation
        assessment_evaluation = AssessmentEvaluation(
            evaluation_id=str(uuid4()),
            assessment_id=assessment_id,
            candidate_id=candidate_id,
            overall_score=overall_score,
            question_evaluations=question_evaluations,
            strengths=list(set(strengths))[:3],  # Deduplicate and limit to top 3
            areas_for_improvement=list(set(areas_for_improvement))[:3]
        )
        
        logger.info(f"Assessment evaluation complete: overall_score={overall_score}")
        return assessment_evaluation
    
    def _mock_evaluate_response(self, question: Question, reference_answer: ReferenceAnswer, 
                               candidate_response: CandidateResponse) -> Tuple[float, str, Dict[str, float]]:
        """Create a mock evaluation for demonstration purposes."""
        # Simulate evaluation by randomly matching key points
        import random
        
        key_points_matched = {}
        for key_point in reference_answer.key_points:
            # Randomly determine if key point is matched (in reality, this would be LLM-based)
            match_score = random.uniform(0.5, 1.0) if random.random() > 0.3 else random.uniform(0, 0.5)
            key_points_matched[key_point] = match_score
        
        # Calculate score based on key point matches and scoring rubric
        score = 0
        for key_point, match_score in key_points_matched.items():
            # Find weight for this key point in scoring rubric if available
            weight = reference_answer.scoring_rubric.get(key_point, 1.0 / len(reference_answer.key_points))
            score += match_score * weight * 100
        
        # Ensure score is between 0 and 100
        score = min(100, max(0, score))
        
        # Generate feedback
        if score >= 80:
            feedback = "Excellent response that covers most key points. Shows strong understanding."
        elif score >= 60:
            feedback = "Good response with some key points addressed. Some areas could be improved."
        elif score >= 40:
            feedback = "Adequate response but missing several key points. Needs more thorough understanding."
        else:
            feedback = "Response is insufficient and missing most key points. Significant improvement needed."
        
        return score, feedback, key_points_matched
    
    def _parse_evaluation_result(self, result: str) -> Tuple[float, str]:
        """Parse the evaluation result to extract score and feedback."""
        # In a real implementation, we would structure the LLM output and parse it
        # For now, return mock values
        return 75.0, "Mock feedback from evaluation"