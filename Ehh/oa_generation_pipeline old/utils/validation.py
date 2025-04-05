# utils/validation.py
import logging
import json
from typing import Dict, Any, List, Optional, Union, Tuple
from pathlib import Path
import jsonschema
from jsonschema import validate, ValidationError

logger = logging.getLogger("validation")

# Schema definitions
RESUME_SCHEMA = {
    "type": "object",
    "required": ["name", "contact", "technical_skills"],
    "properties": {
        "name": {"type": "string"},
        "contact": {
            "type": "object",
            "properties": {
                "phone": {"type": "string"},
                "email": {"type": "string"},
                "linkedin": {"type": "string"},
                "twitter": {"type": "string"},
                "github": {"type": "string"}
            }
        },
        "education": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "institution": {"type": "string"},
                    "degree": {"type": "string"},
                    "location": {"type": "string"},
                    "duration": {"type": "string"}
                },
                "required": ["institution"]
            }
        },
        "experience": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "company": {"type": "string"},
                    "location": {"type": "string"},
                    "duration": {"type": "string"},
                    "responsibilities": {
                        "type": "array",
                        "items": {"type": "string"}
                    }
                },
                "required": ["title", "company"]
            }
        },
        "projects": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "details": {
                        "type": "array",
                        "items": {"type": "string"}
                    }
                },
                "required": ["name"]
            }
        },
        "technical_skills": {
            "type": "object",
            "properties": {
                "languages": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "frameworks_technologies": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "developer_tools": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "data_analysis": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "mathematics": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "research_documentation": {
                    "type": "array",
                    "items": {"type": "string"}
                }
            }
        }
    }
}

JOB_DESCRIPTION_SCHEMA = {
    "type": "object",
    "required": ["title", "requirements", "required_skills"],
    "properties": {
        "title": {"type": "string"},
        "company": {"type": "string"},
        "location": {"type": "string"},
        "description": {"type": "string"},
        "requirements": {
            "type": "array",
            "items": {"type": "string"}
        },
        "responsibilities": {
            "type": "array",
            "items": {"type": "string"}
        },
        "required_skills": {
            "type": "array",
            "items": {"type": "string"}
        },
        "preferred_skills": {
            "type": "array",
            "items": {"type": "string"}
        }
    }
}

QUESTION_TEMPLATE_SCHEMA = {
    "type": "object",
    "required": ["template_id", "category", "subcategory", "question_type", "difficulty", "template_text"],
    "properties": {
        "template_id": {"type": "string"},
        "category": {"type": "string", "enum": ["core_cs", "domain_specific"]},
        "subcategory": {"type": "string"},
        "question_type": {"type": "string", "enum": ["multiple_choice", "coding", "short_answer", "open_ended"]},
        "difficulty": {"type": "string", "enum": ["easy", "medium", "hard", "expert"]},
        "template_text": {"type": "string"},
        "variables": {
            "type": "object",
            "additionalProperties": {
                "type": "array",
                "items": {"type": "string"}
            }
        },
        "requires_skills": {
            "type": "array",
            "items": {"type": "string"}
        }
    }
}

def validate_json(data: Dict[str, Any], schema_type: str) -> Tuple[bool, Optional[str]]:
    """Validate JSON data against a schema."""
    try:
        if schema_type == "resume":
            schema = RESUME_SCHEMA
        elif schema_type == "job_description":
            schema = JOB_DESCRIPTION_SCHEMA
        elif schema_type == "question_template":
            schema = QUESTION_TEMPLATE_SCHEMA
        else:
            return False, f"Unknown schema type: {schema_type}"
        
        validate(instance=data, schema=schema)
        logger.info(f"Successfully validated {schema_type} data")
        return True, None
    
    except ValidationError as e:
        error_message = f"Validation error: {str(e)}"
        logger.error(error_message)
        return False, error_message
    
    except Exception as e:
        error_message = f"Error validating {schema_type} data: {str(e)}"
        logger.error(error_message)
        return False, error_message

def load_and_validate_json(file_path: Path, schema_type: str) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """Load JSON data from a file and validate it against a schema."""
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        is_valid, error_message = validate_json(data, schema_type)
        if is_valid:
            return data, None
        else:
            return None, error_message
    
    except json.JSONDecodeError as e:
        error_message = f"Error decoding JSON from {file_path}: {str(e)}"
        logger.error(error_message)
        return None, error_message
    
    except Exception as e:
        error_message = f"Error loading JSON from {file_path}: {str(e)}"
        logger.error(error_message)
        return None, error_message

def validate_dependencies(data: Dict[str, Any], dependencies: List[Tuple[str, str, List[str]]]) -> Tuple[bool, Optional[str]]:
    """
    Validate that dependencies exist in the data.
    
    Args:
        data: The data to validate
        dependencies: List of tuples (field, required_if_field, required_if_values)
            field: The field to check if it exists
            required_if_field: The field to check the value of
            required_if_values: The values of required_if_field that require field to exist
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        for field, required_if_field, required_if_values in dependencies:
            if required_if_field in data and data[required_if_field] in required_if_values:
                if field not in data:
                    return False, f"Field '{field}' is required when '{required_if_field}' is '{data[required_if_field]}'."
        
        return True, None
    
    except Exception as e:
        error_message = f"Error validating dependencies: {str(e)}"
        logger.error(error_message)
        return False, error_message