"""
SeekerProfile model - detailed seeker information
"""
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4
from sqlmodel import Field, SQLModel, Column, JSON


class SeekerProfile(SQLModel, table=True):
    """
    Detailed profile for job seekers
    Linked to User via user_id
    """
    __tablename__ = "seeker_profiles"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", unique=True, index=True)
    
    # Profile information
    headline: Optional[str] = Field(default=None, max_length=500)
    location: Optional[str] = Field(default=None, max_length=255)
    bio: Optional[str] = Field(default=None, max_length=2000)
    
    # Work preferences stored as JSON
    preferences: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    
    # Questionnaire completion tracking
    questionnaire_completed: bool = Field(default=False)
    questionnaire_completed_at: Optional[datetime] = Field(default=None)
    
    # Stats card (computed from answers)
    stats_card: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    stats_computed_at: Optional[datetime] = Field(default=None)
    
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "headline": "Senior Software Engineer",
                "location": "San Francisco, CA",
                "bio": "Passionate about building scalable systems",
                "preferences": {
                    "remote": True,
                    "desired_role": "Backend Engineer",
                    "salary_min": 120000,
                    "willing_to_relocate": False
                },
                "stats_card": {
                    "attributes": [
                        {"name": "technical_skills", "score": 8.5},
                        {"name": "communication", "score": 7.8},
                        {"name": "problem_solving", "score": 9.0}
                    ]
                }
            }
        }
