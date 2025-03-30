# services/data_integration.py
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

from models.candidate import CandidateProfile

logger = logging.getLogger("data_integration")

class DataIntegrationService:
    """Service to standardize and normalize inputs from ATS and JD modules."""
    
    def __init__(self):
        logger.info("Initializing Data Integration Service")
    
    def load_resume(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Load resume data from a JSON file."""
        try:
            logger.info(f"Loading resume from {file_path}")
            with open(file_path, 'r') as f:
                resume_data = json.load(f)
            logger.info(f"Successfully loaded resume for {resume_data.get('name', 'Unknown')}")
            return resume_data
        except Exception as e:
            logger.error(f"Error loading resume from {file_path}: {str(e)}")
            return None
    
    def load_job_description(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Load job description data from a JSON file."""
        try:
            logger.info(f"Loading job description from {file_path}")
            with open(file_path, 'r') as f:
                jd_data = json.load(f)
            logger.info(f"Successfully loaded job description for {jd_data.get('title', 'Unknown')}")
            return jd_data
        except Exception as e:
            logger.error(f"Error loading job description from {file_path}: {str(e)}")
            return None
    
    def normalize_resume(self, resume_data: Dict[str, Any]) -> Optional[CandidateProfile]:
        """Normalize resume data into a CandidateProfile model."""
        try:
            logger.info(f"Normalizing resume for {resume_data.get('name', 'Unknown')}")
            normalized_profile = CandidateProfile(**resume_data)
            logger.info(f"Successfully normalized resume for {normalized_profile.name}")
            return normalized_profile
        except Exception as e:
            logger.error(f"Error normalizing resume: {str(e)}")
            return None
    
    def validate_data(self, data: Dict[str, Any], schema_type: str) -> bool:
        """Validate incoming data against a schema."""
        # In a real implementation, we would use a schema validation library
        logger.info(f"Validating {schema_type} data")
        if schema_type == "resume":
            required_fields = ["name", "contact", "technical_skills"]
        elif schema_type == "job_description":
            required_fields = ["title", "requirements", "company"]
        else:
            logger.error(f"Unknown schema type: {schema_type}")
            return False
        
        for field in required_fields:
            if field not in data:
                logger.error(f"Missing required field: {field}")
                return False
        
        logger.info(f"Successfully validated {schema_type} data")
        return True