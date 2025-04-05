# tests/test_assessment.py

import pytest
from agents.assessment_agent import AssessmentAgent
from models.data_models import Assessment, CodingQuestion
import os

@pytest.fixture
def assessment_agent():
    return AssessmentAgent(os.getenv("REASONING_API_KEY"))

def test_evaluate_response(assessment_agent):
    question = CodingQuestion(
        id="test1",
        type="coding",
        text="What is Big O notation?",
        difficulty="medium",
        score=10,
        options=["O(1)", "O(n)", "O(n²)", "O(log n)"],
        correct_option=1,
        explanation="Explanation"
    )
    
    assessment = Assessment(
        id="test_assessment",
        candidate_name="John Doe",
        job_title="Software Engineer",
        coding_questions=[question],
        system_design_questions=[],
        behavioral_questions=[],
        total_score=10,
        passing_score=7
    )
    
    responses = {"test1": 1}  # Correct answer
    
    result = assessment_agent.evaluate_response(assessment, responses)
    assert result.passed
    assert result.score > 0