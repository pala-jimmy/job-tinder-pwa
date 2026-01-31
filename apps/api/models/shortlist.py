"""
Shortlist model - saved candidates by offerers
"""
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4
from sqlmodel import Field, SQLModel


class Shortlist(SQLModel, table=True):
    """
    Offerer's saved candidates (liked and shortlisted)
    """
    __tablename__ = "shortlists"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    offerer_id: UUID = Field(foreign_key="offerers.id", index=True)
    seeker_id: UUID = Field(foreign_key="seekers.id", index=True)
    added_at: datetime = Field(default_factory=datetime.utcnow)
    notes: Optional[str] = Field(default=None, max_length=1000)
    
    class Config:
        json_schema_extra = {
            "example": {
                "offerer_id": "123e4567-e89b-12d3-a456-426614174000",
                "seeker_id": "987fcdeb-51a2-43f1-9c8d-123456789abc",
                "notes": "Strong technical background, good culture fit"
            }
        }
