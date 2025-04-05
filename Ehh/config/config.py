# config/config.py
import os
from pathlib import Path
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
SAMPLE_DIR = DATA_DIR / "sample"
OUTPUT_DIR = DATA_DIR / "output"

# Override paths from environment variables if provided
SAMPLE_DIR = Path(os.environ.get("SAMPLE_DIR", SAMPLE_DIR))
OUTPUT_DIR = Path(os.environ.get("OUTPUT_DIR", OUTPUT_DIR))

# Ensure directories exist
SAMPLE_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Sample data paths
RESUME_DIR = Path(os.environ.get("RESUME_DIR", SAMPLE_DIR / "resumes"))
JD_DIR = Path(os.environ.get("JD_DIR", SAMPLE_DIR / "job_descriptions"))
TEMPLATE_DIR = Path(os.environ.get("TEMPLATE_DIR", SAMPLE_DIR / "templates"))

# Ensure sample data directories exist
RESUME_DIR.mkdir(parents=True, exist_ok=True)
JD_DIR.mkdir(parents=True, exist_ok=True)
TEMPLATE_DIR.mkdir(parents=True, exist_ok=True)

# Get logging level from environment variable
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
LOG_LEVEL_MAP = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL
}
LOGGING_LEVEL = LOG_LEVEL_MAP.get(LOG_LEVEL, logging.INFO)

# Replace the current LLM configuration code with this simpler version
API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
REASONING_MODEL = os.environ.get("REASONING_MODEL", "openai/o3-mini")
NON_REASONING_MODEL = os.environ.get("NON_REASONING_MODEL", "gemini-flash-2.0")

# Change this line in config/config.py
LLM_PROVIDER = os.environ.get("LLM_PROVIDER", "mock")  # Change to "mock" for testing

# And update these to match
LLM_CONFIG = {
    "provider": LLM_PROVIDER,
    "api_key": os.environ.get("OPENROUTER_REASONING_API_KEY", ""),
    "model_name": REASONING_MODEL,
    "is_reasoning": True
}

NON_REASONING_LLM_CONFIG = {
    "provider": LLM_PROVIDER,
    "api_key": os.environ.get("OPENROUTER_NON_REASONING_API_KEY", ""),
    "model_name": NON_REASONING_MODEL,
    "is_reasoning": False
}

# Question template categories
QUESTION_CATEGORIES = {
    "core_cs": ["os", "dbms", "dsa", "networking"],
    "domain_specific": ["web_dev", "machine_learning", "data_engineering", "cloud"]
}

# Difficulty levels
DIFFICULTY_LEVELS = ["easy", "medium", "hard", "expert"]