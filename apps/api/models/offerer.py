"""
Offerer model - represents recruiters/employers
"""
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4
from sqlmodel import Field, SQLModel


class Offerer(SQLModel, table=True):
    """
    Recruiter/employer who swipes candidates
    """
    __tablename__ = "offerers"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: str = Field(unique=True, index=True, max_length=255)
    company: str = Field(max_length=255)
    role_filter: Optional[str] = Field(default=None, max_length=255)
    
    # Selected role configuration for feed sorting
    role_config_id: Optional[UUID] = Field(default=None, foreign_key="offerer_role_configs.id")
    
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "email": "recruiter@company.com",
                "company": "Tech Corp",
                "role_filter": "Senior Developer",
                "role_config_id": "456e7890-a12b-34c5-d678-901234567890"
            }
        }
