"""
Questionnaire routes for fetching questionnaires and submitting answers
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from uuid import UUID

from database import get_session
from models import Questionnaire, Question, Answer, User, SeekerProfile
from schemas.questionnaire import (
    QuestionnaireResponse,
    QuestionResponse,
    AnswerSubmission,
    AnswerSubmissionRequest,
    AnswerSubmissionResponse,
)
from auth import get_current_active_user


router = APIRouter(prefix="/questionnaire", tags=["Questionnaire"])


@router.get("", response_model=QuestionnaireResponse)
async def get_questionnaire(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get the active questionnaire with all questions.
    Available to both seekers and offerers.
    """
    # Get the first active questionnaire (in production, you might have multiple)
    statement = select(Questionnaire).where(Questionnaire.is_active == True).limit(1)
    questionnaire = session.exec(statement).first()
    
    if not questionnaire:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active questionnaire found"
        )
    
    # Get all questions for this questionnaire, ordered by order field
    questions_statement = (
        select(Question)
        .where(Question.questionnaire_id == questionnaire.id)
        .order_by(Question.order)
    )
    questions = session.exec(questions_statement).all()
    
    # Convert to response models
    question_responses = [
        QuestionResponse(
            id=q.id,
            questionnaire_id=q.questionnaire_id,
            text=q.text,
            question_type=q.question_type,
            order=q.order,
            options=q.options,
            scoring_config=q.scoring_config,
            is_required=True  # Default to required
        )
        for q in questions
    ]
    
    return QuestionnaireResponse(
        id=questionnaire.id,
        title=questionnaire.name,  # Use 'name' from model
        description=questionnaire.description,
        version=str(questionnaire.version),
        is_active=questionnaire.is_active,
        questions=question_responses
    )


@router.post("/answers", response_model=AnswerSubmissionResponse)
async def submit_answers(
    request: AnswerSubmissionRequest,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """
    Submit or update answers for the current user.
    Supports autosave - repeated submissions will upsert answers.
    Only available to seekers.
    """
    # Verify user is a seeker
    if current_user.role.value != "seeker":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only seekers can submit questionnaire answers"
        )
    
    # Get or create seeker profile
    profile_statement = select(SeekerProfile).where(SeekerProfile.user_id == current_user.id)
    seeker_profile = session.exec(profile_statement).first()
    
    if not seeker_profile:
        # Create profile if it doesn't exist
        seeker_profile = SeekerProfile(user_id=current_user.id)
        session.add(seeker_profile)
        session.commit()
        session.refresh(seeker_profile)
    
    # Get the active questionnaire to count total questions
    questionnaire_statement = select(Questionnaire).where(Questionnaire.is_active == True).limit(1)
    questionnaire = session.exec(questionnaire_statement).first()
    
    if not questionnaire:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active questionnaire found"
        )
    
    # Count total questions in questionnaire
    total_questions_statement = select(Question).where(Question.questionnaire_id == questionnaire.id)
    total_questions = len(session.exec(total_questions_statement).all())
    
    updated_count = 0
    
    # Process each answer submission
    for answer_submission in request.answers:
        # Verify question exists and belongs to active questionnaire
        question = session.get(Question, answer_submission.question_id)
        if not question or question.questionnaire_id != questionnaire.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid question_id: {answer_submission.question_id}"
            )
        
        # Check if answer already exists (upsert logic)
        existing_answer_statement = (
            select(Answer)
            .where(Answer.seeker_profile_id == seeker_profile.id)
            .where(Answer.question_id == answer_submission.question_id)
        )
        existing_answer = session.exec(existing_answer_statement).first()
        
        if existing_answer:
            # Update existing answer
            existing_answer.answer_value = {"value": answer_submission.value}
            session.add(existing_answer)
        else:
            # Create new answer
            new_answer = Answer(
                seeker_profile_id=seeker_profile.id,
                question_id=answer_submission.question_id,
                answer_value={"value": answer_submission.value}
            )
            session.add(new_answer)
        
        updated_count += 1
    
    session.commit()
    
    # Count how many questions have been answered
    answered_statement = (
        select(Answer)
        .where(Answer.seeker_profile_id == seeker_profile.id)
        .join(Question)
        .where(Question.questionnaire_id == questionnaire.id)
    )
    answered_questions = len(session.exec(answered_statement).all())
    
    # Calculate completion percentage
    completion_percent = (answered_questions / total_questions * 100) if total_questions > 0 else 0
    
    # Update questionnaire_completed flag if 100%
    if completion_percent >= 100:
        seeker_profile.questionnaire_completed = True
        session.add(seeker_profile)
        session.commit()
    
    return AnswerSubmissionResponse(
        total_questions=total_questions,
        answered_questions=answered_questions,
        completion_percent=round(completion_percent, 2),
        updated_answers=updated_count
    )
