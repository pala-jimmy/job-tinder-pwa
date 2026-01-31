"""
Pydantic schemas for questionnaire endpoints
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from uuid import UUID
from models.questionnaire import QuestionType


# Response schemas
class QuestionResponse(BaseModel):
    """Schema for question data in questionnaire response"""
    id: UUID
    questionnaire_id: UUID
    text: str
    question_type: QuestionType
    order: int
    options: Optional[Dict[str, Any]] = None
    scoring_config: Optional[Dict[str, Any]] = None
    is_required: bool = True
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "questionnaire_id": "123e4567-e89b-12d3-a456-426614174001",
                "text": "Rate your Python programming skills",
                "question_type": "SCALE",
                "order": 1,
                "options": {"min": 1, "max": 5, "labels": {"1": "Beginner", "5": "Expert"}},
                "scoring_config": {"attribute": "technical_skills", "weight": 1.0},
                "is_required": True
            }
        }


class QuestionnaireResponse(BaseModel):
    """Schema for questionnaire with all questions"""
    id: UUID
    title: str
    description: Optional[str] = None
    version: str = "1.0"
    is_active: bool = True
    questions: List[QuestionResponse] = []
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174001",
                "title": "General Skills Assessment",
                "description": "Evaluate your professional skills",
                "version": "1.0",
                "is_active": True,
                "questions": []
            }
        }


# Request schemas for submitting answers
class AnswerSubmission(BaseModel):
    """Schema for submitting a single answer"""
    question_id: UUID
    value: Any  # Can be int, str, list, etc. depending on question type
    
    class Config:
        json_schema_extra = {
            "example": {
                "question_id": "123e4567-e89b-12d3-a456-426614174000",
                "value": 4
            }
        }


class AnswerSubmissionRequest(BaseModel):
    """Schema for submitting multiple answers at once"""
    answers: List[AnswerSubmission]
    
    class Config:
        json_schema_extra = {
            "example": {
                "answers": [
                    {"question_id": "123e4567-e89b-12d3-a456-426614174000", "value": 4},
                    {"question_id": "123e4567-e89b-12d3-a456-426614174001", "value": "Yes"}
                ]
            }
        }


class AnswerSubmissionResponse(BaseModel):
    """Schema for answer submission response"""
    total_questions: int
    answered_questions: int
    completion_percent: float
    updated_answers: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "total_questions": 16,
                "answered_questions": 8,
                "completion_percent": 50.0,
                "updated_answers": 2
            }
        }
