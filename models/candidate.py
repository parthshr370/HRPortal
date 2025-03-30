# models/candidate.py
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field

class ContactInfo(BaseModel):
    phone: Optional[str] = None
    email: Optional[str] = None
    linkedin: Optional[str] = None
    twitter: Optional[str] = None
    github: Optional[str] = None

class Education(BaseModel):
    institution: str
    degree: Optional[str] = None
    board: Optional[str] = None
    location: Optional[str] = None
    duration: Optional[str] = None

class Experience(BaseModel):
    title: str
    company: str
    location: Optional[str] = None
    duration: Optional[str] = None
    responsibilities: List[str] = []

class Project(BaseModel):
    name: str
    details: List[str] = []

class TechnicalSkills(BaseModel):
    languages: List[str] = []
    frameworks_technologies: List[str] = []
    developer_tools: List[str] = []
    data_analysis: List[str] = []
    mathematics: List[str] = []
    research_documentation: List[str] = []

class CandidateProfile(BaseModel):
    name: str
    contact: ContactInfo
    education: List[Education] = []
    experience: List[Experience] = []
    projects: List[Project] = []
    technical_skills: TechnicalSkills

class SkillMap(BaseModel):
    """Analyzed skills with weights based on experience and projects."""
    core_skills: Dict[str, float] = {}  # Skill name -> weight
    domain_skills: Dict[str, float] = {}
    inferred_skills: Dict[str, float] = {}
    project_validated_skills: List[str] = []

class NormalizedCandidate(BaseModel):
    """Normalized candidate profile with analyzed skill map."""
    profile: CandidateProfile
    skill_map: SkillMap
    experience_level: str = "entry"  # entry, mid, senior
    domain_expertise: List[str] = []