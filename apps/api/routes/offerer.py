"""
Offerer endpoints - config, feed, swipe, shortlist
"""
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select, and_, or_, func
from datetime import datetime

from database import get_session
from models import (
    User, UserRole, Offerer, SeekerProfile, 
    OffererRoleConfig, SwipeDecision, SwipeAction
)
from schemas.offerer import (
    OffererConfigRequest, OffererConfigResponse,
    CandidateCard, FeedResponse,
    SwipeRequest, SwipeResponse,
    ShortlistCandidate, ShortlistResponse,
    NoteRequest, NoteResponse,
    RoleConfigSummary, RoleConfigsResponse
)
from auth import get_current_active_user

router = APIRouter(prefix="/offerer", tags=["offerer"])


def require_offerer(current_user: User = Depends(get_current_active_user)) -> User:
    """Dependency to ensure user is an offerer"""
    if current_user.role != UserRole.OFFERER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only offerers can access this endpoint"
        )
    return current_user



@router.get("/role-configs", response_model=RoleConfigsResponse)
async def list_role_configs(
    db: Session = Depends(get_session)
):
    """
    List all available role configurations
    Public endpoint - no auth required
    """
    statement = select(OffererRoleConfig).where(OffererRoleConfig.is_active == True).order_by(OffererRoleConfig.role_name)
    configs = db.exec(statement).all()
    
    config_summaries = [
        RoleConfigSummary(
            id=config.id,
            role_name=config.role_name,
            description=config.description,
            weights=config.weights
        )
        for config in configs
    ]
    
    return RoleConfigsResponse(
        configs=config_summaries,
        total=len(config_summaries)
    )

@router.put("/config", response_model=OffererConfigResponse)
async def set_offerer_config(
    config_request: OffererConfigRequest,
    current_user: User = Depends(require_offerer),
    db: Session = Depends(get_session)
):
    """
    T5.1 - Set offerer's role configuration for feed sorting
    """
    # Get offerer profile
    statement = select(Offerer).where(Offerer.email == current_user.email)
    offerer = db.exec(statement).first()
    
    if not offerer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Offerer profile not found"
        )
    
    # Verify role config exists
    role_config_statement = select(OffererRoleConfig).where(
        and_(
            OffererRoleConfig.id == config_request.role_config_id,
            OffererRoleConfig.is_active == True
        )
    )
    role_config = db.exec(role_config_statement).first()
    
    if not role_config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role configuration not found or inactive"
        )
    
    # Update offerer's role_config_id
    offerer.role_config_id = config_request.role_config_id
    db.add(offerer)
    db.commit()
    db.refresh(offerer)
    
    return OffererConfigResponse(
        role_config_id=role_config.id,
        role_name=role_config.role_name,
        message=f"Feed will now be sorted by '{role_config.role_name}' role fit"
    )


@router.get("/feed", response_model=FeedResponse)
async def get_candidate_feed(
    cursor: Optional[str] = Query(None, description="Cursor for pagination (seeker_profile_id)"),
    limit: int = Query(10, ge=1, le=50, description="Number of results per page"),
    current_user: User = Depends(require_offerer),
    db: Session = Depends(get_session)
):
    """
    T5.2 - Get paginated feed of candidates sorted by fit score
    Excludes already-swiped candidates
    """
    # Get offerer profile
    statement = select(Offerer).where(Offerer.email == current_user.email)
    offerer = db.exec(statement).first()
    
    if not offerer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Offerer profile not found"
        )
    
    if not offerer.role_config_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please set role configuration first using PUT /offerer/config"
        )
    
    # Get role config for weight calculations
    role_config = db.get(OffererRoleConfig, offerer.role_config_id)
    if not role_config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role configuration not found"
        )
    
    # Get IDs of already-swiped seekers
    swiped_seeker_ids_statement = select(SwipeDecision.seeker_profile_id).where(
        SwipeDecision.offerer_id == offerer.id
    )
    swiped_seeker_ids = {row for row in db.exec(swiped_seeker_ids_statement)}
    
    # Build base query for seekers with computed stats
    base_statement = select(SeekerProfile).where(
        and_(
            SeekerProfile.questionnaire_completed == True,
            SeekerProfile.stats_card.is_not(None),
            SeekerProfile.id.not_in(swiped_seeker_ids) if swiped_seeker_ids else True
        )
    )
    
    # Apply cursor pagination
    if cursor:
        try:
            cursor_uuid = UUID(cursor)
            base_statement = base_statement.where(SeekerProfile.id > cursor_uuid)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid cursor format"
            )
    
    # Order by ID for deterministic pagination (we'll sort by fit score in Python)
    base_statement = base_statement.order_by(SeekerProfile.id).limit(limit + 1)
    
    seekers = db.exec(base_statement).all()
    
    # Check if there are more results
    has_more = len(seekers) > limit
    if has_more:
        seekers = seekers[:limit]
    
    # Compute fit scores and build candidate cards
    candidates = []
    for seeker in seekers:
        if not seeker.stats_card or "fit_scores" not in seeker.stats_card:
            continue
        
        fit_scores = seeker.stats_card.get("fit_scores", {})
        role_fit_score = fit_scores.get(role_config.role_name, 0.0)
        
        candidates.append({
            "seeker": seeker,
            "fit_score": role_fit_score
        })
    
    # Sort by fit score (descending)
    candidates.sort(key=lambda x: x["fit_score"], reverse=True)
    
    # Build response
    candidate_cards = [
        CandidateCard(
            seeker_profile_id=c["seeker"].id,
            headline=c["seeker"].headline,
            location=c["seeker"].location,
            bio=c["seeker"].bio,
            stats=c["seeker"].stats_card.get("stats", {}),
            fit_score=c["fit_score"],
            questionnaire_completed=c["seeker"].questionnaire_completed,
            stats_computed_at=c["seeker"].stats_computed_at
        )
        for c in candidates
    ]
    
    next_cursor = None
    if has_more and seekers:
        next_cursor = str(seekers[-1].id)
    
    return FeedResponse(
        candidates=candidate_cards,
        next_cursor=next_cursor,
        has_more=has_more
    )


@router.post("/swipe", response_model=SwipeResponse)
async def swipe_candidate(
    swipe_request: SwipeRequest,
    current_user: User = Depends(require_offerer),
    db: Session = Depends(get_session)
):
    """
    T5.3 - Record swipe decision (like/pass) on candidate
    """
    # Get offerer profile
    statement = select(Offerer).where(Offerer.email == current_user.email)
    offerer = db.exec(statement).first()
    
    if not offerer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Offerer profile not found"
        )
    
    # Validate decision
    valid_decisions = ["like", "pass"]
    if swipe_request.decision.lower() not in valid_decisions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid decision. Must be one of: {', '.join(valid_decisions)}"
        )
    
    # Verify seeker exists
    seeker = db.get(SeekerProfile, swipe_request.seeker_profile_id)
    if not seeker:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Seeker not found"
        )
    
    # Check if already swiped
    existing_swipe_statement = select(SwipeDecision).where(
        and_(
            SwipeDecision.offerer_id == offerer.id,
            SwipeDecision.seeker_profile_id == swipe_request.seeker_profile_id
        )
    )
    existing_swipe = db.exec(existing_swipe_statement).first()
    
    if existing_swipe:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Already swiped on this candidate"
        )
    
    # Map decision to SwipeAction
    action_map = {
        "like": SwipeAction.LIKE,
        "pass": SwipeAction.PASS
    }
    
    # Create swipe decision
    swipe_decision = SwipeDecision(
        offerer_id=offerer.id,
        seeker_profile_id=swipe_request.seeker_profile_id,
        action=action_map[swipe_request.decision.lower()],
        role_config_id=offerer.role_config_id,
        swiped_at=datetime.utcnow()
    )
    
    db.add(swipe_decision)
    db.commit()
    
    message = "Candidate added to shortlist" if swipe_request.decision.lower() == "like" else "Candidate passed"
    
    return SwipeResponse(
        success=True,
        message=message,
        seeker_profile_id=swipe_request.seeker_profile_id,
        decision=swipe_request.decision.lower()
    )


@router.get("/shortlist", response_model=ShortlistResponse)
async def get_shortlist(
    current_user: User = Depends(require_offerer),
    db: Session = Depends(get_session)
):
    """
    T5.3 - Get all liked (shortlisted) candidates
    """
    # Get offerer profile
    statement = select(Offerer).where(Offerer.email == current_user.email)
    offerer = db.exec(statement).first()
    
    if not offerer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Offerer profile not found"
        )
    
    # Get role config if set (for fit score calculation)
    role_config = None
    if offerer.role_config_id:
        role_config = db.get(OffererRoleConfig, offerer.role_config_id)
    
    # Get all liked swipes
    swipe_statement = select(SwipeDecision, SeekerProfile).join(
        SeekerProfile,
        SwipeDecision.seeker_profile_id == SeekerProfile.id
    ).where(
        and_(
            SwipeDecision.offerer_id == offerer.id,
            SwipeDecision.action == SwipeAction.LIKE
        )
    ).order_by(SwipeDecision.swiped_at.desc())
    
    results = db.exec(swipe_statement).all()
    
    # Build candidate list
    candidates = []
    for swipe, seeker in results:
        # Compute fit score
        fit_score = 0.0
        if seeker.stats_card and "fit_scores" in seeker.stats_card and role_config:
            fit_scores = seeker.stats_card.get("fit_scores", {})
            fit_score = fit_scores.get(role_config.role_name, 0.0)
        
        candidates.append(ShortlistCandidate(
            seeker_profile_id=seeker.id,
            headline=seeker.headline,
            location=seeker.location,
            bio=seeker.bio,
            stats=seeker.stats_card.get("stats", {}) if seeker.stats_card else {},
            fit_score=fit_score,
            note=swipe.note,
            swiped_at=swipe.swiped_at
        ))
    
    return ShortlistResponse(
        candidates=candidates,
        total=len(candidates)
    )


@router.post("/shortlist/{seeker_profile_id}/note", response_model=NoteResponse)
async def add_shortlist_note(
    seeker_profile_id: UUID,
    note_request: NoteRequest,
    current_user: User = Depends(require_offerer),
    db: Session = Depends(get_session)
):
    """
    T5.3 - Add or update note for shortlisted candidate
    """
    # Get offerer profile
    statement = select(Offerer).where(Offerer.email == current_user.email)
    offerer = db.exec(statement).first()
    
    if not offerer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Offerer profile not found"
        )
    
    # Find the swipe decision
    swipe_statement = select(SwipeDecision).where(
        and_(
            SwipeDecision.offerer_id == offerer.id,
            SwipeDecision.seeker_profile_id == seeker_profile_id,
            SwipeDecision.action == SwipeAction.LIKE
        )
    )
    swipe = db.exec(swipe_statement).first()
    
    if not swipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not in shortlist. Must swipe 'like' first."
        )
    
    # Update note
    swipe.note = note_request.note
    db.add(swipe)
    db.commit()
    
    return NoteResponse(
        success=True,
        message="Note added successfully",
        seeker_profile_id=seeker_profile_id
    )



