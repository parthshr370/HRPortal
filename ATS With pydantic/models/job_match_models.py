from typing import Dict, List, Optional
from pydantic import BaseModel, Field, field_validator

class AnalysisBreakdown(BaseModel):
    score: float = 0.0
    details: List[str] = Field(default_factory=lambda: ["No analysis available yet"])

    @field_validator('score')
    def validate_score(cls, v):
        return max(0.0, min(1.0, v))  # Ensure score is between 0 and 1

class MatchAnalysis(BaseModel):
    overall_match_score: float = 0.0
    skills_match: AnalysisBreakdown = Field(default_factory=lambda: AnalysisBreakdown(
        score=0.0,
        details=["Skills analysis not yet performed"]
    ))
    experience_match: AnalysisBreakdown = Field(default_factory=lambda: AnalysisBreakdown(
        score=0.0,
        details=["Experience analysis not yet performed"]
    ))
    education_match: AnalysisBreakdown = Field(default_factory=lambda: AnalysisBreakdown(
        score=0.0,
        details=["Education analysis not yet performed"]
    ))
    additional_insights: List[str] = Field(default_factory=lambda: ["Analysis pending - please process a resume and job description"])
    recommended_interview_questions: Optional[List[str]] = Field(default_factory=lambda: ["No interview questions generated yet"])

    @field_validator('overall_match_score')
    def validate_overall_score(cls, v):
        return max(0.0, min(1.0, v))  # Ensure score is between 0 and 1