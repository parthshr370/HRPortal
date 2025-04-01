from typing import List, Optional, Union
from pydantic import BaseModel, Field

class Education(BaseModel):
    degree: str = "Not specified"
    institution: str = "Not specified"
    graduation_year: Optional[int] = None
    gpa: Optional[float] = None  # Changed to Optional[float]
    field: Optional[str] = None
    graduation_date: Optional[str] = None

class Experience(BaseModel):
    title: str = "Position not specified"
    company: str = "Company not specified"
    duration: str = "Duration not specified"
    description: List[str] = Field(default_factory=lambda: ["Experience details pending"])
    location: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    responsibilities: Optional[List[str]] = Field(default_factory=list)
    achievements: Optional[List[str]] = Field(default_factory=list)

class PersonalInfo(BaseModel):
    name: str = "Name not provided"
    email: str = "Email not provided"
    phone: Optional[str] = None
    location: Optional[str] = None

class Project(BaseModel):
    name: str = "Project name not specified"
    description: Optional[str] = None
    technologies: Optional[List[str]] = Field(default_factory=list)
    url: Optional[str] = None

class Certification(BaseModel):
    name: str = "Certification not specified"
    issuer: Optional[str] = None
    date: Optional[str] = None

class ParsedResume(BaseModel):
    personal_info: PersonalInfo = Field(default_factory=PersonalInfo)
    summary: Optional[str] = "Resume summary pending"
    education: List[Education] = Field(default_factory=list)
    experience: List[Experience] = Field(default_factory=list)
    skills: List[str] = Field(default_factory=list)  # Changed to ensure it's a list
    projects: Optional[List[Project]] = Field(default_factory=list)
    certifications: Optional[List[Certification]] = Field(default_factory=list)

    class Config:
        validate_assignment = True