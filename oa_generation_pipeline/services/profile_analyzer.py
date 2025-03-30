# services/profile_analyzer.py
import logging
from typing import Dict, List, Any, Optional
import json

from langchain_community.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

from models.candidate import CandidateProfile, SkillMap, NormalizedCandidate
from config.config import NON_REASONING_LLM_CONFIG

logger = logging.getLogger("profile_analyzer")

class ProfileAnalyzerService:
    """Service to analyze candidate profiles and create skill maps."""
    
    def __init__(self, llm_config: Dict[str, Any] = None):
        """Initialize the service with LLM configuration."""
        logger.info("Initializing Profile Analyzer Service")
        
        # Use non-reasoning configuration by default
        self.llm_config = llm_config if llm_config else NON_REASONING_LLM_CONFIG
        
        # In a real implementation, we would initialize the LLM here
        # For now, we'll just log that we're using a mock LLM
        logger.info(f"Using {self.llm_config.get('provider')} for profile analysis with model {self.llm_config.get('model_name')}")
    
    def analyze_profile(self, profile: CandidateProfile) -> NormalizedCandidate:
        """Analyze a candidate profile and create a normalized profile with skill map."""
        logger.info(f"Analyzing profile for {profile.name}")
        
        # Create a skill map from the profile
        skill_map = self._create_skill_map(profile)
        
        # Determine experience level
        experience_level = self._determine_experience_level(profile)
        
        # Determine domain expertise
        domain_expertise = self._determine_domain_expertise(profile, skill_map)
        
        # Create normalized candidate
        normalized_candidate = NormalizedCandidate(
            profile=profile,
            skill_map=skill_map,
            experience_level=experience_level,
            domain_expertise=domain_expertise
        )
        
        logger.info(f"Successfully analyzed profile for {profile.name}")
        logger.info(f"Experience level: {experience_level}")
        logger.info(f"Domain expertise: {domain_expertise}")
        
        return normalized_candidate
    
    def _create_skill_map(self, profile: CandidateProfile) -> SkillMap:
        """Create a skill map from a candidate profile."""
        logger.info(f"Creating skill map for {profile.name}")
        
        # In a real implementation, we would use the LLM to analyze skills
        # For now, we'll just create a simple skill map
        
        # Extract skills from technical_skills
        core_skills = {}
        domain_skills = {}
        
        # Process programming languages
        for lang in profile.technical_skills.languages:
            core_skills[lang.lower()] = 0.8  # Assuming proficiency
        
        # Process frameworks and technologies
        for tech in profile.technical_skills.frameworks_technologies:
            domain_skills[tech.lower()] = 0.7  # Assuming proficiency
        
        # Process experience
        for exp in profile.experience:
            for resp in exp.responsibilities:
                # Look for skill keywords in responsibilities
                words = set(resp.lower().split())
                for lang in profile.technical_skills.languages:
                    if lang.lower() in words:
                        core_skills[lang.lower()] = min(1.0, core_skills.get(lang.lower(), 0) + 0.1)  # Boost if mentioned in experience
                
                for tech in profile.technical_skills.frameworks_technologies:
                    if tech.lower() in words:
                        domain_skills[tech.lower()] = min(1.0, domain_skills.get(tech.lower(), 0) + 0.1)  # Boost if mentioned in experience
        
        # Process projects
        project_validated_skills = []
        for project in profile.projects:
            for detail in project.details:
                # Look for skill keywords in project details
                words = set(detail.lower().split())
                for lang in profile.technical_skills.languages:
                    if lang.lower() in words and lang not in project_validated_skills:
                        project_validated_skills.append(lang)
                
                for tech in profile.technical_skills.frameworks_technologies:
                    if tech.lower() in words and tech not in project_validated_skills:
                        project_validated_skills.append(tech)
        
        # Create SkillMap
        skill_map = SkillMap(
            core_skills=core_skills,
            domain_skills=domain_skills,
            inferred_skills={},  # In a real implementation, we would infer additional skills
            project_validated_skills=project_validated_skills
        )
        
        logger.info(f"Successfully created skill map for {profile.name}")
        return skill_map
    
    def _determine_experience_level(self, profile: CandidateProfile) -> str:
        """Determine the experience level of a candidate."""
        # Count years of experience
        total_years = 0
        for exp in profile.experience:
            if exp.duration:
                # Parse duration string (assuming format like "May 2024 – July 2024")
                try:
                    parts = exp.duration.split('–')
                    if len(parts) == 2:
                        start = parts[0].strip()
                        end = parts[1].strip()
                        # Very simplistic calculation - in a real implementation we would parse dates properly
                        if start and end and 'Present' not in end:
                            total_years += 0.25  # Assume 3 months
                        elif start and 'Present' in end:
                            total_years += 0.5  # Assume 6 months for current jobs
                except Exception as e:
                    logger.warning(f"Error parsing duration {exp.duration}: {str(e)}")
        
        # Determine level based on years
        if total_years < 1:
            return "entry"
        elif total_years < 3:
            return "mid"
        else:
            return "senior"
    
    def _determine_domain_expertise(self, profile: CandidateProfile, skill_map: SkillMap) -> List[str]:
        """Determine the domain expertise of a candidate."""
        domains = []
        
        # Check for data science/ML expertise
        ml_keywords = ["python", "pytorch", "tensorflow", "machine learning", "data science", "pandas", "numpy"]
        if any(keyword in skill_map.core_skills or keyword in skill_map.domain_skills for keyword in ml_keywords):
            domains.append("machine_learning")
        
        # Check for web development expertise
        web_keywords = ["javascript", "html", "css", "react", "node", "web development", "flask", "django"]
        if any(keyword in skill_map.core_skills or keyword in skill_map.domain_skills for keyword in web_keywords):
            domains.append("web_development")
        
        # Check for data engineering expertise
        de_keywords = ["sql", "database", "data engineering", "etl", "spark", "hadoop"]
        if any(keyword in skill_map.core_skills or keyword in skill_map.domain_skills for keyword in de_keywords):
            domains.append("data_engineering")
        
        # In a real implementation, we would use the LLM to determine domains more accurately
        
        return domains