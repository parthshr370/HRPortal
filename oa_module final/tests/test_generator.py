# tests/test_generator.py

import pytest
from agents.question_generator import QuestionGenerator
import os

@pytest.fixture
def question_generator():
    return QuestionGenerator(os.getenv("NON_REASONING_API_KEY"))

def test_generate_coding_questions(question_generator):
    skills = ["Python", "Java"]
    level = "mid"
    
    questions = question_generator.generate_coding_questions(skills, level)
    assert len(questions) > 0
    assert all(q.type == "coding" for q in questions)
    
def test_generate_system_design_questions(question_generator):
    experience = [{"description": "Developed scalable systems"}]
    level = "senior"
    
    questions = question_generator.generate_system_design_questions(experience, level)
    assert len(questions) > 0
    assert all(q.type == "system_design" for q in questions)