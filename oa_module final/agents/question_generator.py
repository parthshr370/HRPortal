# agents/question_generator.py

import json
from typing import List, Dict, Any
from pathlib import Path
from langchain_openai.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from models.data_models import (
    CodingQuestion,
    SystemDesignQuestion,
    BehavioralQuestion,
    Assessment
)

class QuestionGenerator:
    """Agent for generating assessment questions"""
    
    def __init__(self, non_reasoning_api_key: str):
        self.llm = ChatOpenAI(
            model="google/gemini-flash-1.5",
            temperature=0.7,
            openai_api_key=non_reasoning_api_key
        )
        
        self.templates = self._load_templates()
        self._init_prompts()
    
    def _init_prompts(self):
        """Initialize prompt templates"""
        self.coding_prompt = PromptTemplate(
            input_variables=["skills", "level", "template"],
            template="""
            Generate a coding question based on the following:
            Skills: {skills}
            Experience Level: {level}
            Template: {template}
            
            The question should test real-world application of the skills.
            
            Return the question in JSON format with:
            {
                "id": "unique_string",
                "type": "coding",
                "text": "question_text",
                "options": ["option1", "option2", "option3", "option4"],
                "correct_option": 0,
                "explanation": "detailed_explanation",
                "difficulty": "easy/medium/hard",
                "score": integer_between_5_and_15
            }
            """
        )
        
        self.system_design_prompt = PromptTemplate(
            input_variables=["experience", "level", "template"],
            template="""
            Generate a system design question based on:
            Experience: {experience}
            Level: {level}
            Template: {template}
            
            Focus on practical scenarios relevant to the candidate's experience.
            
            Return in JSON format with:
            {
                "id": "unique_string",
                "type": "system_design", 
                "text": "question_text",
                "scenario": "detailed_scenario",
                "expected_components": ["component1", "component2"],
                "evaluation_criteria": ["criterion1", "criterion2"],
                "difficulty": "easy/medium/hard",
                "score": integer_between_10_and_30
            }
            """
        )
        
        self.behavioral_prompt = PromptTemplate(
            input_variables=["resume_data", "job_desc", "template"],
            template="""
            Generate a behavioral question based on:
            Resume: {resume_data}
            Job Description: {job_desc}
            Template: {template}
            
            Create questions that reveal both competency and passion.
            
            Return in JSON format with:
            {
                "id": "unique_string",
                "type": "behavioral",
                "text": "question_text",
                "context": "background_context",
                "evaluation_points": ["point1", "point2"],
                "passion_indicators": ["indicator1", "indicator2"],
                "difficulty": "easy/medium/hard",
                "score": integer_between_5_and_15
            }
            """
        )

    def _load_templates(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load question templates from JSON files"""
        templates = {}
        template_dir = Path(__file__).parent.parent / "templates" / "question_templates"
        
        if not template_dir.exists():
            self._create_default_templates(template_dir)
            
        for template_file in template_dir.glob("*.json"):
            with open(template_file) as f:
                templates[template_file.stem] = json.load(f)
                
        return templates

    def _create_default_templates(self, template_dir: Path):
        """Create default templates if they don't exist"""
        template_dir.mkdir(parents=True, exist_ok=True)
        
        default_templates = {
            "coding_templates.json": [
                {
                    "id": "code_1",
                    "type": "algorithm",
                    "difficulty_range": ["easy", "medium"],
                    "structure": "Given {scenario}, implement {task}"
                }
            ],
            "system_design_templates.json": [
                {
                    "id": "design_1",
                    "type": "architecture",
                    "difficulty_range": ["medium", "hard"],
                    "structure": "Design a system that {requirement}"
                }
            ],
            "behavioral_templates.json": [
                {
                    "id": "behavioral_1",
                    "type": "situation",
                    "difficulty_range": ["medium"],
                    "structure": "Tell me about a time when {situation}"
                }
            ]
        }
        
        for filename, content in default_templates.items():
            template_path = template_dir / filename
            with open(template_path, 'w') as f:
                json.dump(content, f, indent=2)

    def generate_assessment(
        self, 
        candidate_name: str,
        job_title: str,
        skills: List[str],
        experience: List[Dict[str, str]],
        level: str,
        resume_data: Dict[str, Any],
        job_desc: Dict[str, Any]
    ) -> Assessment:
        """Generate a complete assessment package"""
        
        # Generate questions for each category
        coding_questions = self.generate_coding_questions(skills, level)
        system_design_questions = self.generate_system_design_questions(experience, level)
        behavioral_questions = self.generate_behavioral_questions(resume_data, job_desc)
        
        # Calculate total and passing scores
        total_score = sum([q.score for q in coding_questions + system_design_questions + behavioral_questions])
        passing_score = int(total_score * 0.7)  # 70% passing threshold
        
        # Create assessment package
        assessment = Assessment(
            candidate_name=candidate_name,
            job_title=job_title,
            coding_questions=coding_questions,
            system_design_questions=system_design_questions,
            behavioral_questions=behavioral_questions,
            total_score=total_score,
            passing_score=passing_score
        )
        
        return assessment

    def generate_coding_questions(
        self, 
        skills: List[str], 
        level: str,
        count: int = 3
    ) -> List[CodingQuestion]:
        """Generate coding questions based on candidate skills"""
        questions = []
        templates = self.templates.get("coding_templates", [])
        
        for i in range(count):
            template = templates[i % len(templates)]
            result = (self.coding_prompt | self.llm).invoke(
                skills=", ".join(skills),
                level=level,
                template=json.dumps(template)
            )
            
            question_data = json.loads(result.content)
            questions.append(CodingQuestion(**question_data))
            
        return questions

    def generate_system_design_questions(
        self,
        experience: List[Dict[str, str]],
        level: str,
        count: int = 2
    ) -> List[SystemDesignQuestion]:
        """Generate system design questions based on experience"""
        questions = []
        templates = self.templates.get("system_design_templates", [])
        
        for i in range(count):
            template = templates[i % len(templates)]
            result = (self.system_design_prompt | self.llm).invoke(
                experience=json.dumps(experience),
                level=level,
                template=json.dumps(template)
            )
            
            question_data = json.loads(result.content)
            questions.append(SystemDesignQuestion(**question_data))
            
        return questions

    def generate_behavioral_questions(
        self,
        resume_data: Dict[str, Any],
        job_desc: Dict[str, Any],
        count: int = 3
    ) -> List[BehavioralQuestion]:
        """Generate behavioral questions based on resume and JD"""
        questions = []
        templates = self.templates.get("behavioral_templates", [])
        
        for i in range(count):
            template = templates[i % len(templates)]
            result = (self.behavioral_prompt | self.llm).invoke(
                resume_data=json.dumps(resume_data),
                job_desc=json.dumps(job_desc),
                template=json.dumps(template)
            )
            
            question_data = json.loads(result.content)
            questions.append(BehavioralQuestion(**question_data))
            
        return questions