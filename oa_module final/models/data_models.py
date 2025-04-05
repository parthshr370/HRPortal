# models/data_models.py

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

class JobDescription(BaseModel):
    """Job Description model"""
    job_title: str
    location: str
    experience_level: str
    responsibilities: List[str]
    qualifications: List[str]
    preferred_qualifications: Optional[List[str]]

class ResumeData(BaseModel):
    """Resume data model"""
    personal_info: Dict[str, str]
    summary: Optional[str]
    education: List[Dict[str, Any]]
    experience: List[Dict[str, Any]]
    skills: List[str]
    projects: Optional[List[Dict[str, Any]]]
    certifications: Optional[List[str]]

class Question(BaseModel):
    """Base question model"""
    id: str
    type: str
    text: str
    difficulty: str
    score: int

class CodingQuestion(Question):
    """Coding question model"""
    options: List[str]
    correct_option: int
    explanation: str

class SystemDesignQuestion(Question):
    """System design question model"""
    scenario: str
    expected_components: List[str]
    evaluation_criteria: List[str]

class BehavioralQuestion(Question):
    """Behavioral question model"""
    context: str
    evaluation_points: List[str]
    passion_indicators: List[str]

class Assessment(BaseModel):
    """Complete assessment model"""
    id: str = Field(default_factory=lambda: datetime.now().strftime("%Y%m%d_%H%M%S"))
    candidate_name: str
    job_title: str
    coding_questions: List[CodingQuestion]
    system_design_questions: List[SystemDesignQuestion]
    behavioral_questions: List[BehavioralQuestion]
    total_score: int
    passing_score: int

class AssessmentResult(BaseModel):
    """Assessment result model"""
    assessment_id: str
    candidate_name: str
    score: int
    passed: bool
    question_scores: Dict[str, int]
    feedback: Dict[str, str]
    technical_rating: float
    passion_rating: float
    timestamp: datetime = Field(default_factory=datetime.now)