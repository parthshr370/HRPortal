from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# API Keys
NON_REASONING_API_KEY = os.getenv("NON_REASONING_API_KEY")
REASONING_API_KEY = os.getenv("REASONING_API_KEY")

# OpenRouter Configuration
OPENROUTER_API_BASE = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_MODELS_URL = "https://openrouter.ai/api/v1/models"

OPENROUTER_HEADERS = {
    "Content-Type": "application/json",
    "HTTP-Referer": "http://localhost:5000",  # Your site URL
    "X-Title": "ATS Portal",  # Your site name
    "OpenAI-Organization": "OPENROUTER"  # Required for OpenRouter
}

# Model Configuration
MODELS = {
    "non_reasoning": {
        "name": "google/gemini-2.0-flash-001",
        "api_key": NON_REASONING_API_KEY,
        "temperature": 0.1,
        "max_tokens": 1000
    },
    "reasoning": {
        "name": "openai/o3-mini",
        "api_key": REASONING_API_KEY,
        "temperature": 0.2,
        "max_tokens": 2000
    }
}

# Supported File Types
SUPPORTED_FILE_TYPES = {
    "application/pdf": "pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
    "text/plain": "txt"
}

# Matching Weights
MATCHING_WEIGHTS = {
    "skills": 0.4,
    "experience": 0.3,
    "education": 0.2,
    "additional": 0.1
}

# Rate Limiting
RATE_LIMIT = {
    "max_requests_per_minute": 10,
    "burst_limit": 20
}

# Error Messages
ERROR_MESSAGES = {
    "api_error": "OpenRouter API error: {}",
    "file_error": "Error processing file: {}",
    "validation_error": "Validation error: {}",
    "rate_limit_error": "Rate limit exceeded. Please try again later."
}