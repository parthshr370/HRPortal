import logging
from typing import Dict, List, Any, Optional
from uuid import uuid4

from models.question import Question, ReferenceAnswer, QuestionType
from config.config import LLM_CONFIG  # Default is reasoning configuration

logger = logging.getLogger("answer_validator")

# ... existing code ... 