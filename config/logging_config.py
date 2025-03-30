# config/logging_config.py
import logging
import sys
from pathlib import Path

from config.config import BASE_DIR

# Create logs directory
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

# Configure logging
def setup_logging(log_level=logging.INFO):
    """Configure logging for the application."""
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    
    # Configure root logger
    logging.basicConfig(
        level=log_level,
        format=log_format,
        datefmt=date_format,
        handlers=[
            # Console handler
            logging.StreamHandler(sys.stdout),
            # File handler
            logging.FileHandler(LOG_DIR / "oa_generation.log")
        ]
    )
    
    # Create loggers for each module
    loggers = {
        "data_integration": logging.getLogger("data_integration"),
        "profile_analyzer": logging.getLogger("profile_analyzer"),
        "question_generator": logging.getLogger("question_generator"),
        "answer_generator": logging.getLogger("answer_generator"),
        "evaluator": logging.getLogger("evaluator"),
        "persistence": logging.getLogger("persistence"),
        "main": logging.getLogger("main")
    }
    
    # Set level for all loggers
    for logger in loggers.values():
        logger.setLevel(log_level)
    
    return loggers