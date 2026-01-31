"""
Swipe model - tracks offerer actions on candidates
"""
from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4
from sqlmodel import Field, SQLModel


class SwipeAction(str, Enum):
    """Possible swipe actions"""
    LIKE = "like"
    DISLIKE = "dislike"
    PASS = "pass"


class Swipe(SQLModel, table=True):
    """
    Record of offerer swiping on a seeker
    """
    __tablename__ = "swipes"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    offerer_id: UUID = Field(foreign_key="offerers.id", index=True)
    seeker_id: UUID = Field(foreign_key="seekers.id", index=True)
    action: SwipeAction = Field(max_length=20)
    swiped_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "offerer_id": "123e4567-e89b-12d3-a456-426614174000",
                "seeker_id": "987fcdeb-51a2-43f1-9c8d-123456789abc",
                "action": "like"
            }
        }
