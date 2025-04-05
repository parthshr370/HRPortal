# models/assessment.py
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from datetime import datetime
from uuid import uuid4

from models.question import Question, ReferenceAnswer

class Assessment(BaseModel):
    """Online assessment created for a candidate."""
    assessment_id: str = Field(default_factory=lambda: str(uuid4()))
    candidate_id: str
    job_id: str
    created_at: datetime = Field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    status: str = "created"  # created, sent, in_progress, completed
    questions: List[Question] = []
    reference_answers: List[ReferenceAnswer] = []
    metadata: Dict[str, Any] = {}

class CandidateResponse(BaseModel):
    """Candidate's response to a question."""
    response_id: str = Field(default_factory=lambda: str(uuid4()))
    question_id: str
    candidate_id: str
    content: str
    submitted_at: datetime = Field(default_factory=datetime.now)
