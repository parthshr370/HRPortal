# test_run.py

import pytest
import asyncio
from main import OAModule

@pytest.fixture
def sample_markdown():
    return """
# Job Description
Title: Software Engineer
Location: Remote
Experience: 5+ years

Requirements:
- Strong Python programming skills
- Experience with web development
- Knowledge of system design

# Resume
Name: John Doe
Email: john@example.com
Skills: Python, Django, React, System Design
Experience:
- Senior Developer at Tech Corp (3 years)
  - Led team of 5 developers
  - Implemented scalable solutions
- Developer at StartUp Inc (2 years)
  - Full-stack development
  - API design and implementation
    """

@pytest.mark.asyncio
async def test_assessment_generation(sample_markdown):
    oa_module = OAModule()
    assessment = await oa_module.process_input(sample_markdown)
    
    assert assessment is not None
    assert assessment.candidate_name == "John Doe"
    assert len(assessment.coding_questions) > 0
    assert len(assessment.system_design_questions) > 0
    assert len(assessment.behavioral_questions) > 0

@pytest.mark.asyncio
async def test_response_evaluation(sample_markdown):
    oa_module = OAModule()
    assessment = await oa_module.process_input(sample_markdown)
    
    # Create sample responses
    responses = {
        question.id: "Sample response for " + question.id
        for question in (
            assessment.coding_questions +
            assessment.system_design_questions +
            assessment.behavioral_questions
        )
    }
    
    result = await oa_module.evaluate_responses(assessment, responses)
    assert result is not None
    assert result.candidate_name == "John Doe"
    assert result.score >= 0
    
    report = oa_module.generate_report(result)
    assert report is not None
    assert isinstance(report, str)
    assert len(report) > 0

if __name__ == "__main__":
    pytest.main([__file__, "-v"])