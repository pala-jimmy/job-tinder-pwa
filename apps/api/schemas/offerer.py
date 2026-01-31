"""
Offerer endpoint schemas
"""
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field
from datetime import datetime


class OffererConfigRequest(BaseModel):
    """Request to set offerer's role configuration"""
    role_config_id: UUID = Field(..., description="ID of the role configuration to use for feed sorting")


class OffererConfigResponse(BaseModel):
    """Response after setting role configuration"""
    role_config_id: UUID
    role_name: str
    message: str = "Role configuration updated successfully"


class CandidateCard(BaseModel):
    """Candidate card for feed (no contact details)"""
    seeker_profile_id: UUID
    headline: Optional[str] = None
    location: Optional[str] = None
    bio: Optional[str] = None
    
    # Computed stats
    stats: dict = Field(..., description="Attribute scores (0-100)")
    fit_score: float = Field(..., description="Fit score for selected role (0-100)")
    
    # Metadata
    questionnaire_completed: bool
    stats_computed_at: Optional[datetime] = None


class FeedResponse(BaseModel):
    """Paginated feed of candidates"""
    candidates: List[CandidateCard]
    next_cursor: Optional[str] = Field(None, description="Cursor for next page (seeker_profile_id)")
    has_more: bool = Field(..., description="Whether there are more results")


class SwipeRequest(BaseModel):
    """Request to swipe on a candidate"""
    seeker_profile_id: UUID
    decision: str = Field(..., description="Swipe decision: 'like' or 'pass'")


class SwipeResponse(BaseModel):
    """Response after swiping"""
    success: bool
    message: str
    seeker_profile_id: UUID
    decision: str


class ShortlistCandidate(BaseModel):
    """Candidate in shortlist with additional details"""
    seeker_profile_id: UUID
    headline: Optional[str] = None
    location: Optional[str] = None
    bio: Optional[str] = None
    
    # Stats
    stats: dict
    fit_score: float
    
    # Shortlist metadata
    note: Optional[str] = None
    swiped_at: datetime


class ShortlistResponse(BaseModel):
    """List of shortlisted candidates"""
    candidates: List[ShortlistCandidate]
    total: int


class NoteRequest(BaseModel):
    """Request to add/update note for shortlisted candidate"""
    note: str = Field(..., max_length=2000, description="Note about the candidate")


class NoteResponse(BaseModel):
    """Response after adding/updating note"""
    success: bool
    message: str
    seeker_profile_id: UUID

class RoleConfigSummary(BaseModel):
    """Summary of a role configuration"""
    id: UUID
    role_name: str
    description: Optional[str] = None
    weights: dict
    
    
class RoleConfigsResponse(BaseModel):
    """List of available role configurations"""
    configs: List[RoleConfigSummary]
    total: int
