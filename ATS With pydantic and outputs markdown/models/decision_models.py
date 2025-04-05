from typing import List, Optional
from enum import Enum
from pydantic import BaseModel, Field, validator

class DecisionStatus(str, Enum):
    PROCEED = "PROCEED"
    HOLD = "HOLD"
    REJECT = "REJECT"

class DecisionDetails(BaseModel):
    status: str = DecisionStatus.HOLD
    confidence_score: int = 30
    interview_stage: str = "SCREENING"

    @validator('confidence_score')
    def validate_confidence(cls, v):
        return max(0, min(100, v))  # Ensure confidence is between 0 and 100

class RationaleDetails(BaseModel):
    key_strengths: List[str] = Field(default_factory=lambda: ["Pending resume analysis"])
    concerns: List[str] = Field(default_factory=lambda: ["Resume analysis not yet completed"])
    risk_factors: List[str] = Field(default_factory=lambda: ["Unable to assess risk factors until analysis is complete"])

class RecommendationDetails(BaseModel):
    interview_focus: List[str] = Field(default_factory=lambda: ["Complete resume analysis required before providing interview focus areas"])
    skill_verification: List[str] = Field(default_factory=lambda: ["Skills verification pending resume processing"])
    discussion_points: List[str] = Field(default_factory=lambda: ["Discussion points will be generated after resume analysis"])

class HiringManagerNotes(BaseModel):
    salary_band_fit: str = "Pending assessment"
    growth_trajectory: str = "To be evaluated"
    team_fit_considerations: str = "Awaiting team fit analysis"
    onboarding_requirements: List[str] = Field(default_factory=lambda: ["Complete candidate profile required for onboarding assessment"])

class NextStepsDetails(BaseModel):
    immediate_actions: List[str] = Field(default_factory=lambda: ["Upload and process resume", "Add job description", "Run analysis"])
    required_approvals: List[str] = Field(default_factory=lambda: ["Initial screening pending"])
    timeline_recommendation: str = "Analysis required before timeline can be determined"

class DecisionFeedback(BaseModel):
    decision: DecisionDetails = Field(default_factory=DecisionDetails)
    rationale: RationaleDetails = Field(default_factory=RationaleDetails)
    recommendations: RecommendationDetails = Field(default_factory=RecommendationDetails)
    hiring_manager_notes: HiringManagerNotes = Field(default_factory=HiringManagerNotes)
    next_steps: NextStepsDetails = Field(default_factory=NextStepsDetails) 