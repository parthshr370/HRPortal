# agents/question_generator.py

import json
import os
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
            openai_api_key=non_reasoning_api_key,
            openai_api_base="https://openrouter.ai/api/v1"
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
            try:
                with open(template_file) as f:
                    template_data = json.load(f)
                    
                    # Check if the templates are in the expected format
                    if "templates" in template_data:
                        templates[template_file.stem] = template_data["templates"]
                    else:
                        templates[template_file.stem] = template_data
            except Exception as e:
                print(f"Error loading template file {template_file}: {e}")
                # Create a default template
                if template_file.stem == "coding_templates":
                    templates[template_file.stem] = self._create_default_coding_templates()
                elif template_file.stem == "system_design_templates":
                    templates[template_file.stem] = self._create_default_system_design_templates()
                elif template_file.stem == "behavioral_templates":
                    templates[template_file.stem] = self._create_default_behavioral_templates()
        
        # Ensure we have defaults for all template types
        if "coding_templates" not in templates or not templates["coding_templates"]:
            templates["coding_templates"] = self._create_default_coding_templates()
            
        if "system_design_templates" not in templates or not templates["system_design_templates"]:
            templates["system_design_templates"] = self._create_default_system_design_templates()
            
        if "behavioral_templates" not in templates or not templates["behavioral_templates"]:
            templates["behavioral_templates"] = self._create_default_behavioral_templates()
                
        return templates

    def _create_default_templates(self, template_dir: Path):
        """Create default templates if they don't exist"""
        template_dir.mkdir(parents=True, exist_ok=True)
        
        # Coding templates
        coding_file = template_dir / "coding_templates.json"
        if not coding_file.exists():
            with open(coding_file, 'w') as f:
                json.dump({"templates": self._create_default_coding_templates()}, f, indent=2)
        
        # System design templates
        design_file = template_dir / "system_design_templates.json"
        if not design_file.exists():
            with open(design_file, 'w') as f:
                json.dump({"templates": self._create_default_system_design_templates()}, f, indent=2)
                
        # Behavioral templates
        behavioral_file = template_dir / "behavioral_templates.json"
        if not behavioral_file.exists():
            with open(behavioral_file, 'w') as f:
                json.dump({"templates": self._create_default_behavioral_templates()}, f, indent=2)

    def _create_default_coding_templates(self) -> List[Dict[str, Any]]:
        """Create default coding question templates"""
        return [
            {
                "id": "code_algo",
                "type": "algorithm",
                "text": "What is the most efficient data structure for {task}?",
                "options_template": ["Array", "Hash Table", "Tree", "Graph"]
            },
            {
                "id": "code_debug",
                "type": "debugging",
                "text": "What's wrong with this code snippet?\n```python\n{code}\n```",
                "options_template": ["Option A", "Option B", "Option C", "Option D"]
            }
        ]
        
    def _create_default_system_design_templates(self) -> List[Dict[str, Any]]:
        """Create default system design question templates"""
        return [
            {
                "id": "design_arch",
                "type": "architecture",
                "text": "Design a system that can {requirement}."
            },
            {
                "id": "design_scale",
                "type": "scalability",
                "text": "How would you scale {system} to handle {load}?"
            }
        ]
        
    def _create_default_behavioral_templates(self) -> List[Dict[str, Any]]:
        """Create default behavioral question templates"""
        return [
            {
                "id": "behavioral_situation",
                "type": "situation",
                "text": "Tell me about a time when you {situation}."
            },
            {
                "id": "behavioral_teamwork",
                "type": "collaboration",
                "text": "Describe a situation where you had to {challenge} with a team."
            }
        ]

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
        
        # Ensure we have templates to work with
        coding_templates = self.templates.get("coding_templates", [])
        if not coding_templates:
            coding_templates = self._create_default_coding_templates()
        
        for i in range(count):
            try:
                # Get a template, cycling through available ones
                template_index = i % len(coding_templates)
                template = coding_templates[template_index]
                
                # Generate question
                prompt_result = self.llm.invoke(self.coding_prompt.format(
                    skills=", ".join(skills) if skills else "Programming",
                    level=level,
                    template=json.dumps(template)
                ))
                
                # Extract JSON
                question_text = prompt_result.content
                
                # Clean JSON from markdown blocks if present
                if "```json" in question_text:
                    question_text = question_text.split("```json", 1)[1].split("```", 1)[0]
                elif "```" in question_text:
                    question_text = question_text.split("```", 1)[0]
                
                question_data = json.loads(question_text.strip())
                
                # Create question object
                questions.append(CodingQuestion(**question_data))
                
            except Exception as e:
                print(f"Error generating coding question {i+1}: {e}")
                # Create a default question
                questions.append(CodingQuestion(
                    id=f"coding_{i+1}",
                    type="coding",
                    text=f"What data structure would you use to implement a cache?",
                    options=["Array", "Hash Table", "Linked List", "Binary Tree"],
                    correct_option=1,
                    explanation="Hash Tables provide O(1) average time complexity for lookups, which is ideal for caches.",
                    difficulty="medium",
                    score=10
                ))
            
        return questions

    def generate_system_design_questions(
        self,
        experience: List[Dict[str, str]],
        level: str,
        count: int = 2
    ) -> List[SystemDesignQuestion]:
        """Generate system design questions based on experience"""
        questions = []
        
        # Ensure we have templates to work with
        design_templates = self.templates.get("system_design_templates", [])
        if not design_templates:
            design_templates = self._create_default_system_design_templates()
        
        for i in range(count):
            try:
                # Get a template, cycling through available ones
                template_index = i % len(design_templates)
                template = design_templates[template_index]
                
                # Generate question
                prompt_result = self.llm.invoke(self.system_design_prompt.format(
                    experience=json.dumps(experience) if experience else "[]",
                    level=level,
                    template=json.dumps(template)
                ))
                
                # Extract JSON
                question_text = prompt_result.content
                
                # Clean JSON from markdown blocks if present
                if "```json" in question_text:
                    question_text = question_text.split("```json", 1)[1].split("```", 1)[0]
                elif "```" in question_text:
                    question_text = question_text.split("```", 1)[0]
                
                question_data = json.loads(question_text.strip())
                
                # Create question object
                questions.append(SystemDesignQuestion(**question_data))
                
            except Exception as e:
                print(f"Error generating system design question {i+1}: {e}")
                # Create a default question
                questions.append(SystemDesignQuestion(
                    id=f"design_{i+1}",
                    type="system_design",
                    text="Design a scalable web service that can handle high traffic loads",
                    scenario="You are tasked with designing a web service that needs to handle millions of requests per day with high availability and low latency.",
                    expected_components=["Load Balancer", "Web Servers", "Database", "Caching Layer"],
                    evaluation_criteria=["Scalability", "Availability", "Performance", "Cost"],
                    difficulty="medium",
                    score=15
                ))
            
        return questions

    def generate_behavioral_questions(
        self,
        resume_data: Dict[str, Any],
        job_desc: Dict[str, Any],
        count: int = 3
    ) -> List[BehavioralQuestion]:
        """Generate behavioral questions based on resume and JD"""
        questions = []
        
        # Ensure we have templates to work with
        behavioral_templates = self.templates.get("behavioral_templates", [])
        if not behavioral_templates:
            behavioral_templates = self._create_default_behavioral_templates()
        
        for i in range(count):
            try:
                # Get a template, cycling through available ones
                template_index = i % len(behavioral_templates)
                template = behavioral_templates[template_index]
                
                # Generate question
                prompt_result = self.llm.invoke(self.behavioral_prompt.format(
                    resume_data=json.dumps(resume_data),
                    job_desc=json.dumps(job_desc),
                    template=json.dumps(template)
                ))
                
                # Extract JSON
                question_text = prompt_result.content
                
                # Clean JSON from markdown blocks if present
                if "```json" in question_text:
                    question_text = question_text.split("```json", 1)[1].split("```", 1)[0]
                elif "```" in question_text:
                    question_text = question_text.split("```", 1)[0]
                
                question_data = json.loads(question_text.strip())
                
                # Create question object
                questions.append(BehavioralQuestion(**question_data))
                
            except Exception as e:
                print(f"Error generating behavioral question {i+1}: {e}")
                # Create a default question
                questions.append(BehavioralQuestion(
                    id=f"behavioral_{i+1}",
                    type="behavioral",
                    text="Tell me about a time when you faced a difficult technical challenge and how you overcame it.",
                    context="This question helps assess problem-solving abilities and resilience.",
                    evaluation_points=["Problem analysis", "Solution approach", "Outcome"],
                    passion_indicators=["Enthusiasm in description", "Learning from experience"],
                    difficulty="medium",
                    score=10
                ))
            
        return questions