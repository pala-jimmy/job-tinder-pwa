"""
Questionnaire models - questions and answers
"""
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4
from sqlmodel import Field, SQLModel, Column, JSON


class QuestionType(str, Enum):
    """Question types for different input formats"""
    MULTIPLE_CHOICE = "multiple_choice"
    SCALE = "scale"  # 1-5 or 1-10
    TEXT = "text"
    YES_NO = "yes_no"


class Question(SQLModel, table=True):
    """
    Individual questionnaire questions
    """
    __tablename__ = "questions"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    questionnaire_id: UUID = Field(foreign_key="questionnaires.id", index=True)
    
    # Question content
    text: str = Field(max_length=1000)
    question_type: QuestionType = Field(max_length=50)
    order: int = Field(default=0)  # Display order
    
    # Options for multiple choice questions (JSON array)
    options: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    
    # Scoring configuration
    scoring_config: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "text": "How comfortable are you with public speaking?",
                "question_type": "scale",
                "order": 1,
                "options": {
                    "min": 1,
                    "max": 10,
                    "labels": {
                        "1": "Not comfortable at all",
                        "10": "Very comfortable"
                    }
                },
                "scoring_config": {
                    "attribute": "communication",
                    "weight": 0.3
                }
            }
        }


class Questionnaire(SQLModel, table=True):
    """
    Questionnaire container - groups questions together
    """
    __tablename__ = "questionnaires"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)
    version: int = Field(default=1)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "General Skills Assessment",
                "description": "Basic questionnaire for all seekers",
                "version": 1,
                "is_active": True
            }
        }


class Answer(SQLModel, table=True):
    """
    Seeker answers to questionnaire questions
    """
    __tablename__ = "answers"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    seeker_profile_id: UUID = Field(foreign_key="seeker_profiles.id", index=True)
    question_id: UUID = Field(foreign_key="questions.id", index=True)
    
    # Answer value (stored as JSON to handle different types)
    answer_value: dict = Field(sa_column=Column(JSON))
    
    answered_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "seeker_profile_id": "123e4567-e89b-12d3-a456-426614174000",
                "question_id": "987fcdeb-51a2-43f1-9c8d-123456789abc",
                "answer_value": {
                    "value": 8,
                    "display": "8/10"
                }
            }
        }
