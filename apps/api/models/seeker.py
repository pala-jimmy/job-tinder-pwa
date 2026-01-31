"""
Seeker model - represents job seekers
"""
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4
from sqlmodel import Field, SQLModel, Column, JSON


class Seeker(SQLModel, table=True):
    """
    Job seeker who completes profile and questionnaire
    """
    __tablename__ = "seekers"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: str = Field(unique=True, index=True, max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # JSON fields for flexible data structure
    profile: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    questionnaire_progress: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    stats_card: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "seeker@example.com",
                "profile": {
                    "name": "Jane Doe",
                    "bio": "Experienced software engineer",
                    "work_preferences": {
                        "location": "Remote",
                        "remote": True,
                        "desired_role": "Senior Developer"
                    }
                },
                "questionnaire_progress": {
                    "completed": False,
                    "current_step": 3,
                    "answers": {}
                },
                "stats_card": {
                    "attributes": [
                        {"name": "technical_skills", "score": 8.5},
                        {"name": "communication", "score": 7.2}
                    ],
                    "computed_at": "2026-01-31T12:00:00"
                }
            }
        }
