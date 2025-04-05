# models/evaluation.py
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from datetime import datetime
from uuid import uuid4

class QuestionEvaluation(BaseModel):
    """Evaluation of a candidate's response to a single question."""
    evaluation_id: str = Field(default_factory=lambda: str(uuid4()))
    response_id: str
    question_id: str
    score: float  # 0 to 100
    feedback: str
    confidence: float  # 0 to 1
    key_points_matched: Dict[str, float] = {}  # Key point -> match score
    detailed_feedback: Dict[str, Any] = {}

class AssessmentEvaluation(BaseModel):
    """Overall evaluation of a candidate's assessment."""
    evaluation_id: str = Field(default_factory=lambda: str(uuid4()))
    assessment_id: str
    candidate_id: str
    overall_score: float  # 0 to 100
    question_evaluations: List[QuestionEvaluation] = []
    strengths: List[str] = []
    areas_for_improvement: List[str] = []
    evaluated_at: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, Any] = {}