# config.py

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Keys
NON_REASONING_API_KEY = os.getenv("NON_REASONING_API_KEY")
REASONING_API_KEY = os.getenv("REASONING_API_KEY")

# Model configurations
NON_REASONING_MODEL = "google/gemini-2.0-flash-001"
REASONING_MODEL = "openai/o3-mini"

# File paths
BASE_DIR = Path(__file__).parent
TEMPLATES_DIR = BASE_DIR / "templates"
QUESTION_TEMPLATES_DIR = TEMPLATES_DIR / "question_templates"
PROMPT_TEMPLATES_DIR = TEMPLATES_DIR / "prompt_templates"

# Assessment configuration
ASSESSMENT_CONFIG = {
    "coding_questions": {
        "junior": 2,
        "mid": 3,
        "senior": 4
    },
    "system_design_questions": {
        "junior": 1,
        "mid": 2,
        "senior": 3
    },
    "behavioral_questions": {
        "junior": 2,
        "mid": 3,
        "senior": 3
    },
    "passing_score_percentage": 70
}

# Ensure required directories exist
for directory in [TEMPLATES_DIR, QUESTION_TEMPLATES_DIR, PROMPT_TEMPLATES_DIR]:
    directory.mkdir(parents=True, exist_ok=True)