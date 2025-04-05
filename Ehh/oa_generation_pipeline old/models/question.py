
# models/question.py
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from enum import Enum

class QuestionType(str, Enum):
    MULTIPLE_CHOICE = "multiple_choice"
    CODING = "coding"
    SHORT_ANSWER = "short_answer"
    OPEN_ENDED = "open_ended"

class DifficultyLevel(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    EXPERT = "expert"

class QuestionCategory(str, Enum):
    CORE_CS = "core_cs"
    DOMAIN_SPECIFIC = "domain_specific"

class QuestionTemplate(BaseModel):
    """Template for generating questions."""
    template_id: str
    category: QuestionCategory
    subcategory: str  # e.g., "os", "dbms", "web_dev"
    question_type: QuestionType
    difficulty: DifficultyLevel
    template_text: str
    variables: Dict[str, List[str]] = {}  # Variable name -> possible values
    requires_skills: List[str] = []

class Question(BaseModel):
    """Generated question based on template."""
    question_id: str
    template_id: Optional[str] = None
    category: QuestionCategory
    subcategory: str
    question_type: QuestionType
    difficulty: DifficultyLevel
    content: str
    skills_tested: List[str] = []
    metadata: Dict[str, Any] = {}

class ReferenceAnswer(BaseModel):
    """Reference answer for a generated question."""
    answer_id: str
    question_id: str
    content: str
    key_points: List[str] = []
    scoring_rubric: Dict[str, float] = {}  # Key point -> weight
    explanation: Optional[str] = None