"""
Seeker routes for profile and stats
"""
from typing import Dict, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from uuid import UUID

from database import get_session
from models import User, SeekerProfile
from schemas.seeker import StatsResponse
from auth import get_current_active_user
from services.scoring import compute_stats, compute_all_fit_scores


router = APIRouter(prefix="/seeker", tags=["Seeker"])


@router.get("/stats", response_model=StatsResponse)
async def get_seeker_stats(
    include_fit_scores: bool = True,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get computed stats for the current seeker.
    
    Returns:
        - Attribute scores (0-100) for all attributes
        - Optional: Fit scores for each role configuration
    
    Only available to seekers.
    """
    # Verify user is a seeker
    if current_user.role.value != "seeker":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only seekers can access stats"
        )
    
    # Get seeker profile
    profile_statement = select(SeekerProfile).where(SeekerProfile.user_id == current_user.id)
    seeker_profile = session.exec(profile_statement).first()
    
    if not seeker_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Seeker profile not found. Please complete the questionnaire first."
        )
    
    # Compute attribute stats
    stats = compute_stats(seeker_profile.id, session)
    
    # Optionally compute fit scores for all roles
    fit_scores = None
    if include_fit_scores:
        fit_scores = compute_all_fit_scores(stats, session)
    
    # Update stats_card in profile for caching
    seeker_profile.stats_card = stats
    session.add(seeker_profile)
    session.commit()
    
    return StatsResponse(
        seeker_profile_id=seeker_profile.id,
        stats=stats,
        fit_scores=fit_scores,
        questionnaire_completed=seeker_profile.questionnaire_completed
    )
