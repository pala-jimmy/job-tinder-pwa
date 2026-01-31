"""
Shortlist model - saved candidates by offerers
"""
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4
from sqlmodel import Field, SQLModel


class ShortlistStatus(str, Enum):
    """Shortlist entry status"""
    ACTIVE = "active"
    CONTACTED = "contacted"
    INTERVIEWING = "interviewing"
    REJECTED = "rejected"
    HIRED = "hired"


class Shortlist(SQLModel, table=True):
    """
    Offerer's saved candidates (liked and shortlisted)
    """
    __tablename__ = "shortlists"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    offerer_id: UUID = Field(foreign_key="offerers.id", index=True)
    seeker_profile_id: UUID = Field(foreign_key="seeker_profiles.id", index=True)
    
    # Notes and status tracking
    notes: Optional[str] = Field(default=None, max_length=2000)
    status: ShortlistStatus = Field(default=ShortlistStatus.ACTIVE, max_length=20)
    
    # Rating (optional - offerer can rate 1-5 stars)
    rating: Optional[int] = Field(default=None, ge=1, le=5)
    
    added_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "offerer_id": "123e4567-e89b-12d3-a456-426614174000",
                "seeker_id": "987fcdeb-51a2-43f1-9c8d-123456789abc",
                "notes": "Strong technical background, good culture fit"
            }
        }
