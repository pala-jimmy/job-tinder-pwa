"""
User model - base authentication and role management
"""
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4
from sqlmodel import Field, SQLModel


class UserRole(str, Enum):
    """User role types"""
    SEEKER = "seeker"
    OFFERER = "offerer"
    ADMIN = "admin"


class User(SQLModel, table=True):
    """
    Base user model for authentication
    Both seekers and offerers have a User record
    """
    __tablename__ = "users"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: str = Field(unique=True, index=True, max_length=255)
    hashed_password: str = Field(max_length=255)
    role: UserRole = Field(max_length=20)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = Field(default=None)
    is_active: bool = Field(default=True)
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "role": "seeker",
                "is_active": True
            }
        }
