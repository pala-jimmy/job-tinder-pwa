"""
Pydantic schemas for seeker endpoints
"""
from pydantic import BaseModel
from typing import Dict, Optional
from uuid import UUID


class StatsResponse(BaseModel):
    """Schema for seeker stats response"""
    seeker_profile_id: UUID
    stats: Dict[str, float]  # Attribute name -> score (0-100)
    fit_scores: Optional[Dict[str, float]] = None  # Role name -> fit score (0-100)
    questionnaire_completed: bool
    
    class Config:
        json_schema_extra = {
            "example": {
                "seeker_profile_id": "123e4567-e89b-12d3-a456-426614174000",
                "stats": {
                    "technical_skills": 85.0,
                    "communication": 72.5,
                    "leadership": 60.0,
                    "problem_solving": 90.0,
                    "adaptability": 78.0,
                    "teamwork": 88.0
                },
                "fit_scores": {
                    "Software Engineer": 87.5,
                    "Sales Representative": 65.2,
                    "Team Lead": 73.8
                },
                "questionnaire_completed": True
            }
        }
