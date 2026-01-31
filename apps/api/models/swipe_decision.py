"""
SwipeDecision model - tracking offerer swipe actions
"""
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4
from sqlmodel import Field, SQLModel


class SwipeAction(str, Enum):
    """Swipe action types"""
    LIKE = "like"
    DISLIKE = "dislike"
    PASS = "pass"
    SUPER_LIKE = "super_like"  # Optional: strong interest


class SwipeDecision(SQLModel, table=True):
    """
    Record of offerer swiping on seeker profiles
    Renamed from Swipe for clarity
    """
    __tablename__ = "swipe_decisions"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    offerer_id: UUID = Field(foreign_key="offerers.id", index=True)
    seeker_profile_id: UUID = Field(foreign_key="seeker_profiles.id", index=True)
    
    action: SwipeAction = Field(max_length=20)

    # Optional: which role config was used for this swipe
    role_config_id: Optional[UUID] = Field(default=None, foreign_key="offerer_role_configs.id")

    swiped_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Optional note for shortlisted candidates
    note: Optional[str] = Field(default=None, max_length=2000)

    class Config:
        json_schema_extra = {
            "example": {
                "offerer_id": "123e4567-e89b-12d3-a456-426614174000",
                "seeker_profile_id": "987fcdeb-51a2-43f1-9c8d-123456789abc",
                "action": "like",
                "role_config_id": "456e7890-a12b-34c5-d678-901234567890",
                "note": "Strong technical background, good culture fit"
            }
        }
