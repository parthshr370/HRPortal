# services/question_generator.py
import logging
import json
import random
from pathlib import Path
from typing import Dict, List, Any, Optional
from uuid import uuid4

from models.candidate import NormalizedCandidate
from models.question import QuestionTemplate, Question, QuestionCategory, QuestionType, DifficultyLevel
from config.config import NON_REASONING_LLM_CONFIG

logger = logging.getLogger("question_generator")

class QuestionGeneratorService:
    """Service to generate personalized assessment questions."""
    
    def __init__(self, template_dir: Path, llm_config: Dict[str, Any] = None):
        """Initialize the service with templates directory and LLM configuration."""
        logger.info("Initializing Question Generator Service")
        self.template_dir = template_dir
        
        # Use non-reasoning configuration by default
        self.llm_config = llm_config if llm_config else NON_REASONING_LLM_CONFIG
        
        # Load question templates
        self.templates = self._load_templates()
        
        logger.info(f"Using {self.llm_config.get('provider')} for question generation with model {self.llm_config.get('model_name')}")
        logger.info(f"Loaded {len(self.templates)} question templates")
    
    def _load_templates(self) -> Dict[str, QuestionTemplate]:
        """Load question templates from the templates directory."""
        templates = {}
        try:
            template_files = list(self.template_dir.glob("*.json"))
            logger.info(f"Found {len(template_files)} template files")
            
            for template_file in template_files:
                try:
                    with open(template_file, 'r') as f:
                        template_data = json.load(f)
                        template = QuestionTemplate(**template_data)
                        templates[template.template_id] = template
                        logger.debug(f"Loaded template {template.template_id}")
                except Exception as e:
                    logger.error(f"Error loading template from {template_file}: {str(e)}")
            
            logger.info(f"Successfully loaded {len(templates)} templates")
            return templates
        except Exception as e:
            logger.error(f"Error loading templates: {str(e)}")
            return {}
    
    def generate_questions(self, candidate: NormalizedCandidate, job_requirements: Dict[str, Any], num_questions: int = 5) -> List[Question]:
        """Generate personalized questions for a candidate based on their profile and job requirements."""
        logger.info(f"Generating {num_questions} questions for {candidate.profile.name}")
        
        # Filter templates based on candidate skills and job requirements
        filtered_templates = self._filter_templates(candidate, job_requirements)
        if not filtered_templates:
            logger.warning("No suitable templates found")
            return []
        
        # Select templates for question generation
        selected_templates = self._select_templates(filtered_templates, candidate, job_requirements, num_questions)
        
        # Generate questions from templates
        questions = []
        for template in selected_templates:
            try:
                question = self._generate_question_from_template(template, candidate)
                if question:
                    questions.append(question)
            except Exception as e:
                logger.error(f"Error generating question from template {template.template_id}: {str(e)}")
        
        logger.info(f"Successfully generated {len(questions)} questions")
        return questions
    
    def _filter_templates(self, candidate: NormalizedCandidate, job_requirements: Dict[str, Any]) -> List[QuestionTemplate]:
        """Filter templates based on candidate skills and job requirements."""
        filtered_templates = []
        
        # Get candidate skills
        candidate_skills = set(candidate.skill_map.core_skills.keys()) | set(candidate.skill_map.domain_skills.keys())
        
        # Get job skills (assuming job_requirements has a 'required_skills' field)
        job_skills = set(job_requirements.get("required_skills", []))
        
        for template in self.templates.values():
            # Check if template requires skills that the candidate has
            if any(skill in candidate_skills for skill in template.requires_skills):
                filtered_templates.append(template)
            # Check if template is for job-specific skills
            elif template.category == QuestionCategory.DOMAIN_SPECIFIC and any(skill in job_skills for skill in template.requires_skills):
                filtered_templates.append(template)
        
        logger.info(f"Filtered {len(filtered_templates)} templates based on candidate skills and job requirements")
        return filtered_templates
    
    def _select_templates(self, templates: List[QuestionTemplate], candidate: NormalizedCandidate, job_requirements: Dict[str, Any], num_questions: int) -> List[QuestionTemplate]:
        """Select templates for question generation based on candidate profile and job requirements."""
        # Determine appropriate difficulty based on experience level
        difficulty_mapping = {
            "entry": [DifficultyLevel.EASY, DifficultyLevel.MEDIUM],
            "mid": [DifficultyLevel.MEDIUM, DifficultyLevel.HARD],
            "senior": [DifficultyLevel.HARD, DifficultyLevel.EXPERT]
        }
        appropriate_difficulties = difficulty_mapping.get(candidate.experience_level, [DifficultyLevel.MEDIUM])
        
        # Filter templates by difficulty
        difficulty_filtered = [t for t in templates if t.difficulty in appropriate_difficulties]
        
        # Ensure we have enough templates
        if len(difficulty_filtered) < num_questions:
            # Fallback to all templates
            logger.warning(f"Not enough templates with appropriate difficulty. Using all available templates.")
            difficulty_filtered = templates
        
        # Prioritize templates based on job requirements
        # In a real implementation, we would use a more sophisticated algorithm
        selected_templates = random.sample(difficulty_filtered, min(num_questions, len(difficulty_filtered)))
        
        logger.info(f"Selected {len(selected_templates)} templates for question generation")
        return selected_templates
    
    def _generate_question_from_template(self, template: QuestionTemplate, candidate: NormalizedCandidate) -> Optional[Question]:
        """Generate a question from a template."""
        logger.info(f"Generating question from template {template.template_id}")
        
        # In a real implementation, we would use the LLM to generate the question
        # For now, we'll just substitute variables in the template
        
        question_text = template.template_text
        
        # Replace variables in the template
        for var_name, var_values in template.variables.items():
            if var_values:
                replacement = random.choice(var_values)
                question_text = question_text.replace(f"{{{var_name}}}", replacement)
        
        # Create a question
        question = Question(
            question_id=str(uuid4()),
            template_id=template.template_id,
            category=template.category,
            subcategory=template.subcategory,
            question_type=template.question_type,
            difficulty=template.difficulty,
            content=question_text,
            skills_tested=template.requires_skills
        )
        
        logger.info(f"Successfully generated question {question.question_id}")
        return question