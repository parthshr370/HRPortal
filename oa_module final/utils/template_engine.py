# utils/template_engine.py

from typing import Dict, Any
from pathlib import Path
import json
from jinja2 import Template

class TemplateEngine:
    """Engine for processing question templates"""
    
    def __init__(self, templates_dir: Path):
        self.templates_dir = templates_dir
        self.templates = self._load_templates()
        
    def _load_templates(self) -> Dict[str, Any]:
        """Load all template files"""
        templates = {}
        
        # Load question templates
        question_types = ['coding', 'system_design', 'behavioral', 'personality']
        for q_type in question_types:
            template_file = self.templates_dir / f"{q_type}_templates.json"
            if template_file.exists():
                with open(template_file) as f:
                    templates[q_type] = json.load(f)
            else:
                templates[q_type] = self._create_default_template(q_type)
                with open(template_file, 'w') as f:
                    json.dump(templates[q_type], f, indent=2)
                    
        return templates
        
    def _create_default_template(self, template_type: str) -> Dict[str, Any]:
        """Create default template for given type"""
        defaults = {
            'coding': [
                {
                    "id": "code_1",
                    "type": "algorithm",
                    "template": """
                    Given a problem involving {data_structure}, implement a solution that:
                    1. {requirement_1}
                    2. {requirement_2}
                    
                    Consider the following example:
                    {example}
                    
                    What would be the most efficient approach?
                    """,
                    "difficulty_levels": {
                        "junior": ["arrays", "strings", "basic algorithms"],
                        "mid": ["trees", "graphs", "dynamic programming"],
                        "senior": ["system design", "optimization", "scalability"]
                    }
                }
            ],
            'system_design': [
                {
                    "id": "design_1",
                    "type": "architecture",
                    "template": """
                    Design a system that handles {requirement} with the following constraints:
                    - {constraint_1}
                    - {constraint_2}
                    
                    Consider:
                    1. Scalability
                    2. Reliability
                    3. Security
                    """,
                    "difficulty_levels": {
                        "junior": ["basic services", "simple APIs"],
                        "mid": ["distributed systems", "caching"],
                        "senior": ["complex architectures", "high availability"]
                    }
                }
            ],
            'behavioral': [
                {
                    "id": "behavioral_1",
                    "type": "situation",
                    "template": """
                    Tell me about a time when you {situation}.
                    
                    Consider:
                    - What was the challenge?
                    - How did you approach it?
                    - What was the outcome?
                    """,
                    "categories": [
                        "leadership",
                        "problem-solving",
                        "teamwork",
                        "conflict resolution"
                    ]
                }
            ],
            'personality': [
                {
                    "id": "personality_1",
                    "type": "work_style",
                    "template": """
                    How do you handle {situation} in a professional setting?
                    
                    Consider:
                    - Your typical approach
                    - Past experiences
                    - Lessons learned
                    """,
                    "categories": [
                        "stress management",
                        "time management",
                        "communication style",
                        "adaptation"
                    ]
                }
            ]
        }
        return defaults.get(template_type, [])
        
    def get_template(self, template_type: str, template_id: str) -> Dict[str, Any]:
        """Get specific template by type and ID"""
        templates = self.templates.get(template_type, [])
        for template in templates:
            if template["id"] == template_id:
                return template
        return None
        
    def render_template(
        self,
        template_data: Dict[str, Any],
        context: Dict[str, Any]
    ) -> str:
        """Render template with given context"""
        template = Template(template_data["template"])
        return template.render(**context)
        
    def get_difficulty_level(
        self,
        template_type: str,
        template_id: str,
        experience_level: str
    ) -> str:
        """Get appropriate difficulty level based on experience"""
        template = self.get_template(template_type, template_id)
        if not template or "difficulty_levels" not in template:
            return "medium"
            
        levels = template["difficulty_levels"]
        if experience_level in levels:
            return levels[experience_level]
        return levels.get("mid", "medium")