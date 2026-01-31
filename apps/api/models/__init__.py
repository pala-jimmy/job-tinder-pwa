"""
SQLModel database models
"""
# Core user models
from .user import User, UserRole
from .seeker_profile import SeekerProfile
from .offerer import Offerer

# Questionnaire models
from .questionnaire import Questionnaire, Question, Answer, QuestionType

# Configuration
from .offerer_role_config import OffererRoleConfig

# Actions
from .swipe_decision import SwipeDecision, SwipeAction
from .shortlist import Shortlist, ShortlistStatus

# Legacy models (keeping for migration compatibility)
from .seeker import Seeker
from .swipe import Swipe

__all__ = [
    # Core
    "User",
    "UserRole",
    "SeekerProfile",
    "Offerer",
    # Questionnaire
    "Questionnaire",
    "Question",
    "Answer",
    "QuestionType",
    # Config
    "OffererRoleConfig",
    # Actions
    "SwipeDecision",
    "SwipeAction",
    "Shortlist",
    "ShortlistStatus",
    # Legacy
    "Seeker",
    "Swipe",
]
