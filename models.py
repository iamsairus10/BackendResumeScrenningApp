from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from fastapi import UploadFile


class ResumeData(BaseModel):
    """Model for parsed resume data"""
    skills: List[str]
    experience_years: Optional[int]
    education: List[str]
    full_text: str


class JobDescriptionData(BaseModel):
    """Model for parsed job description data"""
    required_skills: List[str]
    required_experience_years: Optional[int]
    education_requirements: List[str]
    full_text: str


class MatchScoreBreakdown(BaseModel):
    """Model for detailed match score breakdown"""
    skills_score: float
    experience_score: float
    education_score: float
    semantic_score: float


class ScreeningResponse(BaseModel):
    """Model for API response"""
    overall_match_percentage: float
    breakdown: MatchScoreBreakdown
    message: str


class ScreeningRequest(BaseModel):
    """Model for API request validation"""
    jd_text: Optional[str] = None