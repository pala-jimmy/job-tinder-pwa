"""
Pydantic schemas for authentication endpoints
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from uuid import UUID
from models.user import UserRole


# Request schemas
class RegisterRequest(BaseModel):
    """Schema for user registration"""
    email: EmailStr
    password: str = Field(min_length=8, max_length=100)
    role: UserRole = Field(default=UserRole.SEEKER)
    
    # Optional fields for offerer registration
    company: Optional[str] = Field(None, max_length=255, description="Company name (required for offerers)")

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "strongpassword123",
                "role": "seeker",
                "company": "Tech Corp"
            }
        }


class LoginRequest(BaseModel):
    """Schema for user login"""
    email: EmailStr
    password: str

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "strongpassword123"
            }
        }


# Response schemas
class TokenResponse(BaseModel):
    """Schema for token response"""
    access_token: str
    token_type: str = "bearer"

    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer"
            }
        }


class UserResponse(BaseModel):
    """Schema for user data response"""
    id: UUID
    email: str
    role: UserRole
    is_active: bool

    class Config:
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "email": "user@example.com",
                "role": "seeker",
                "is_active": True
            }
        }
