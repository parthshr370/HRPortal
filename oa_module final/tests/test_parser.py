# tests/test_parser.py

import pytest
from agents.parser_agent import ParserAgent
import os

@pytest.fixture
def parser_agent():
    return ParserAgent(os.getenv("NON_REASONING_API_KEY"))

def test_parse_markdown(parser_agent):
    markdown_content = """
    # Job Description
    Title: Software Engineer
    Location: Remote
    Experience: 5+ years
    
    # Resume
    Name: John Doe
    Experience: 6 years
    Skills: Python, Java
    """
    
    result = parser_agent.parse_markdown(markdown_content)
    assert "job_description" in result
    assert "resume_data" in result
    
def test_extract_key_matches(parser_agent):
    parsed_data = {
        "job_description": {
            "qualifications": ["Python", "Java"],
            "responsibilities": ["Develop software"]
        },
        "resume_data": {
            "skills": ["Python", "JavaScript"],
            "experience": [{"description": "Developed software applications"}]
        }
    }
    
    matches = parser_agent.extract_key_matches(parsed_data)
    assert "Python" in matches["skills"]
    assert len(matches["experience"]) > 0

