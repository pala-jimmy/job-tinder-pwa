"""
OffererRoleConfig model - role-specific scoring weights
"""
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4
from sqlmodel import Field, SQLModel, Column, JSON


class OffererRoleConfig(SQLModel, table=True):
    """
    Configuration for different offerer roles
    Defines which attributes matter most for specific roles
    """
    __tablename__ = "offerer_role_configs"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    role_name: str = Field(unique=True, max_length=255, index=True)
    description: Optional[str] = Field(default=None, max_length=1000)
    
    # Scoring weights for different attributes (JSON)
    # e.g., {"technical_skills": 0.4, "communication": 0.3, "leadership": 0.3}
    weights: dict = Field(sa_column=Column(JSON))
    
    # Optional display configuration
    display_config: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "role_name": "Software Engineer",
                "description": "Technical role focused on coding and problem solving",
                "weights": {
                    "technical_skills": 0.40,
                    "problem_solving": 0.30,
                    "communication": 0.20,
                    "leadership": 0.10
                },
                "display_config": {
                    "primary_attributes": ["technical_skills", "problem_solving"],
                    "card_color": "#3b82f6"
                }
            }
        }
