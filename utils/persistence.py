# utils/persistence.py
import json
import logging
import os
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, TypeVar, Type, Generic
from datetime import datetime
from uuid import uuid4

from pydantic import BaseModel

logger = logging.getLogger("persistence")

# Generic type for Pydantic models
T = TypeVar('T', bound=BaseModel)

class FilePersistence(Generic[T]):
    """File-based persistence layer for storing models as JSON files."""
    
    def __init__(self, data_dir: Path, model_class: Type[T], subfolder: str):
        """Initialize the persistence layer."""
        self.data_dir = data_dir / subfolder
        self.model_class = model_class
        self.data_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Initialized file persistence for {model_class.__name__} in {self.data_dir}")
    
    def save(self, model: T) -> bool:
        """Save a model to a JSON file."""
        try:
            # Get ID field from model (assumes model has an ID field ending with '_id')
            id_field = None
            for field in model.__fields__:
                if field.endswith('_id'):
                    id_field = field
                    break
            
            if not id_field:
                logger.error(f"No ID field found in model {self.model_class.__name__}")
                return False
            
            # Get ID value
            id_value = getattr(model, id_field)
            
            # Create filename
            filename = f"{id_value}.json"
            file_path = self.data_dir / filename
            
            # Convert model to JSON
            json_data = model.json(indent=2)
            
            # Write to file
            with open(file_path, 'w') as f:
                f.write(json_data)
            
            logger.info(f"Saved {self.model_class.__name__} with ID {id_value} to {file_path}")
            return True
        
        except Exception as e:
            logger.error(f"Error saving {self.model_class.__name__}: {str(e)}")
            return False
    
    def load(self, id_value: str) -> Optional[T]:
        """Load a model from a JSON file."""
        try:
            # Create filename
            filename = f"{id_value}.json"
            file_path = self.data_dir / filename
            
            # Check if file exists
            if not file_path.exists():
                logger.warning(f"File not found: {file_path}")
                return None
            
            # Read from file
            with open(file_path, 'r') as f:
                json_data = f.read()
            
            # Parse JSON data
            model = self.model_class.parse_raw(json_data)
            
            logger.info(f"Loaded {self.model_class.__name__} with ID {id_value} from {file_path}")
            return model
        
        except Exception as e:
            logger.error(f"Error loading {self.model_class.__name__} with ID {id_value}: {str(e)}")
            return None
    
    def load_all(self) -> List[T]:
        """Load all models from JSON files."""
        try:
            models = []
            for file_path in self.data_dir.glob("*.json"):
                try:
                    with open(file_path, 'r') as f:
                        json_data = f.read()
                    
                    model = self.model_class.parse_raw(json_data)
                    models.append(model)
                
                except Exception as e:
                    logger.error(f"Error loading file {file_path}: {str(e)}")
            
            logger.info(f"Loaded {len(models)} {self.model_class.__name__} models")
            return models
        
        except Exception as e:
            logger.error(f"Error loading all {self.model_class.__name__} models: {str(e)}")
            return []
    
    def delete(self, id_value: str) -> bool:
        """Delete a model JSON file."""
        try:
            # Create filename
            filename = f"{id_value}.json"
            file_path = self.data_dir / filename
            
            # Check if file exists
            if not file_path.exists():
                logger.warning(f"File not found for deletion: {file_path}")
                return False
            
            # Delete file
            os.remove(file_path)
            
            logger.info(f"Deleted {self.model_class.__name__} with ID {id_value}")
            return True
        
        except Exception as e:
            logger.error(f"Error deleting {self.model_class.__name__} with ID {id_value}: {str(e)}")
            return False


def create_sample_data(output_dir: Path) -> None:
    """Create sample data files for development and testing."""
    logger.info("Creating sample data files")
    
    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Create sample resume
    sample_resume = {
        "name": "Parth Sharma",
        "contact": {
            "phone": "9971361784",
            "email": "parthshr370@gmail.com",
            "linkedin": "LinkedIn",
            "twitter": "Twitter",
            "github": "Github"
        },
        "education": [
            {
                "institution": "Manipal University Jaipur",
                "degree": "Bachelor of Technology in Data Science",
                "location": "Jaipur",
                "duration": "Sep 2022 – Present"
            },
            {
                "institution": "Blue Bells Public School",
                "board": "CBSE",
                "location": "Gurugram",
                "duration": "April 2007 – May 2022"
            }
        ],
        "experience": [
            {
                "title": "Research Intern",
                "company": "Indian Institue of Information Technology Allahabad",
                "location": "Allahabad, India",
                "duration": "May 2024 – July 2024",
                "responsibilities": [
                    "Developed a fusion model using LSTM and CNN to improve process prediction.",
                    "Fine-tuned LLMs for process modelling using POWL and PM4PY.",
                    "Enhanced the PromoAI Framework for large scale databases.",
                    "Tech Stack: Pytorch, Langchain, PM4PY, Pandas"
                ]
            }
        ],
        "projects": [
            {
                "name": "HR Portal Agent | Capstone Project",
                "details": [
                    "Developed a distributed multi-agent HR system for OCR-based resume extraction, candidate matching, and interview question generation.",
                    "Employed LangGraph for orchestrating agent workflows and integrated RESTful APIs for asynchronous communication.",
                    "Tools: LangChain, LangGraph, MongoDB, Flask/FastAPI, Docker"
                ]
            },
            {
                "name": "Email AI Agent | Capstone Project",
                "details": [
                    "Built a multi-agent orchestration system to automate email classification and response drafting.",
                    "Integrated SMTP for real-time email sending and coordinated agent workflows using LangGraph.",
                    "Tools: LangChain, LangGraph, LangSmith, DeepSeek API"
                ]
            }
        ],
        "technical_skills": {
            "languages": ["Python", "Java", "SQL", "HTML/CSS", "C"],
            "frameworks_technologies": [
                "PyTorch", "TensorFlow", "PM4PY", "Librosa", "Pandas", "NumPy", 
                "Matplotlib", "PyTorch Lightning", "Keras", "Flask", "Streamlit", "EEGLAB"
            ],
            "developer_tools": [
                "Git", "Docker", "Linux", "LaTeX", "Matlab", "EEGLAB", 
                "PRoM (Process Mining)", "GitHub"
            ],
            "data_analysis": [
                "Signal Processing", "Spectral Analysis", "EEG Data Analysis", 
                "Statistical Analysis", "Machine Learning", "Data Visualization"
            ],
            "mathematics": [
                "Stochastic Modelling", "Linear Algebra", "Calculus", 
                "Advanced Statistics", "Optimization"
            ],
            "research_documentation": [
                "Research Methodology", "Technical Writing", 
                "Project Documentation", "Blogging"
            ]
        }
    }
    
    # Create sample job description
    sample_jd = {
        "title": "Machine Learning Engineer",
        "company": "TechInnovate",
        "location": "Remote",
        "description": "We are looking for a Machine Learning Engineer to join our team and help us build intelligent applications.",
        "requirements": [
            "Bachelor's or Master's degree in Computer Science, Data Science, or a related field",
            "Strong programming skills in Python",
            "Experience with machine learning frameworks such as TensorFlow or PyTorch",
            "Understanding of data structures, algorithms, and software design principles",
            "Experience with data processing and analysis libraries like Pandas and NumPy",
            "Knowledge of database systems"
        ],
        "responsibilities": [
            "Design and implement machine learning models",
            "Analyze and preprocess large datasets",
            "Deploy and monitor machine learning systems",
            "Collaborate with cross-functional teams",
            "Stay up-to-date with the latest research and technologies"
        ],
        "required_skills": [
            "python", "machine_learning", "tensorflow", "pytorch", "pandas", "numpy", 
            "data_analysis", "algorithms"
        ],
        "preferred_skills": [
            "flask", "docker", "cloud_computing", "nlp", "computer_vision"
        ]
    }
    
    # Create sample question templates
    sample_templates = [
        {
            "template_id": "core_cs_dsa_001",
            "category": "core_cs",
            "subcategory": "dsa",
            "question_type": "coding",
            "difficulty": "medium",
            "template_text": "Write a function to find the {order} element in a linked list.",
            "variables": {
                "order": ["kth", "middle", "last", "third-to-last"]
            },
            "requires_skills": ["algorithms", "data_structures", "linked_lists"]
        },
        {
            "template_id": "core_cs_dbms_001",
            "category": "core_cs",
            "subcategory": "dbms",
            "question_type": "open_ended",
            "difficulty": "medium",
            "template_text": "Explain the difference between {concept1} and {concept2} in database management systems. Provide examples of when you would use each.",
            "variables": {
                "concept1": ["normalization", "ACID properties", "indexing", "transactions"],
                "concept2": ["denormalization", "BASE properties", "partitioning", "stored procedures"]
            },
            "requires_skills": ["database", "sql"]
        },
        {
            "template_id": "domain_specific_ml_001",
            "category": "domain_specific",
            "subcategory": "machine_learning",
            "question_type": "short_answer",
            "difficulty": "hard",
            "template_text": "Describe how you would implement {algorithm} from scratch. What are the key challenges?",
            "variables": {
                "algorithm": ["gradient descent", "backpropagation", "k-means clustering", "random forest"]
            },
            "requires_skills": ["machine_learning", "algorithms", "mathematics"]
        },
        {
            "template_id": "domain_specific_ml_002",
            "category": "domain_specific",
            "subcategory": "machine_learning",
            "question_type": "multiple_choice",
            "difficulty": "medium",
            "template_text": "Which of the following is NOT a common way to address overfitting in machine learning models?\n\nA) {option_a}\nB) {option_b}\nC) {option_c}\nD) {option_d}",
            "variables": {
                "option_a": ["Regularization"],
                "option_b": ["Cross-validation"],
                "option_c": ["Feature engineering"],
                "option_d": ["Increasing model complexity"]
            },
            "requires_skills": ["machine_learning", "model_evaluation"]
        }
    ]
    
    # Save sample data
    try:
        # Save resume
        resume_path = output_dir / "sample_resume.json"
        with open(resume_path, 'w') as f:
            json.dump(sample_resume, f, indent=2)
        logger.info(f"Created sample resume at {resume_path}")
        
        # Save job description
        jd_path = output_dir / "sample_jd.json"
        with open(jd_path, 'w') as f:
            json.dump(sample_jd, f, indent=2)
        logger.info(f"Created sample job description at {jd_path}")
        
        # Save question templates
        templates_dir = output_dir / "templates"
        templates_dir.mkdir(exist_ok=True)
        
        for template in sample_templates:
            template_path = templates_dir / f"{template['template_id']}.json"
            with open(template_path, 'w') as f:
                json.dump(template, f, indent=2)
            logger.info(f"Created sample template at {template_path}")
        
        logger.info("Sample data creation complete")
        
    except Exception as e:
        logger.error(f"Error creating sample data: {str(e)}")