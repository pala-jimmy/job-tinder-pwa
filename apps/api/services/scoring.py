"""
Scoring service for computing seeker stats and fit scores
"""
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from uuid import UUID
from sqlmodel import Session, select

from models import Question, Answer, SeekerProfile, OffererRoleConfig


# Load scoring rules from shared package
def load_scoring_rules() -> Dict[str, Any]:
    """Load scoring rules from packages/shared/scoring-rules.json"""
    rules_path = Path(__file__).parent.parent.parent.parent / "packages" / "shared" / "scoring-rules.json"
    
    if not rules_path.exists():
        raise FileNotFoundError(f"Scoring rules not found at {rules_path}")
    
    with open(rules_path, 'r') as f:
        return json.load(f)


def normalize_score(value: float, min_val: float = 0, max_val: float = 5) -> float:
    """
    Normalize a score to 0-100 scale
    
    Args:
        value: The raw value to normalize
        min_val: Minimum possible value
        max_val: Maximum possible value
    
    Returns:
        Normalized score between 0 and 100
    """
    if max_val == min_val:
        return 0.0
    
    normalized = ((value - min_val) / (max_val - min_val)) * 100
    return max(0.0, min(100.0, normalized))  # Clamp to 0-100


def compute_attribute_score(
    answers: List[Answer],
    questions: Dict[UUID, Question],
    attribute: str
) -> float:
    """
    Compute the score for a specific attribute based on answers
    
    Args:
        answers: List of user's answers
        questions: Dictionary mapping question_id to Question objects
        attribute: The attribute to score (e.g., "technical_skills")
    
    Returns:
        Normalized score (0-100) for the attribute
    """
    relevant_answers = []
    total_weight = 0.0
    
    for answer in answers:
        question = questions.get(answer.question_id)
        if not question or not question.scoring_config:
            continue
        
        # Check if this question contributes to the target attribute
        q_attribute = question.scoring_config.get("attribute")
        if q_attribute != attribute:
            continue
        
        weight = question.scoring_config.get("weight", 1.0)
        
        # Extract numeric value from answer
        answer_data = answer.answer_value
        
        # Handle different answer formats
        if isinstance(answer_data, dict):
            # If answer_value is a dict, look for 'value' key
            answer_value = answer_data.get("value", answer_data)
            if isinstance(answer_value, (int, float)):
                value = float(answer_value)
            else:
                continue
        elif isinstance(answer_data, (int, float)):
            value = float(answer_data)
        elif isinstance(answer_data, str):
            # Try to parse string to number
            try:
                value = float(answer_data)
            except ValueError:
                # For text answers, skip or handle differently
                continue
        else:
            continue
        
        # Get min/max from question options
        min_val = 0
        max_val = 5
        if question.options:
            min_val = question.options.get("min", 0)
            max_val = question.options.get("max", 5)
        
        # Normalize and weight
        normalized = normalize_score(value, min_val, max_val)
        relevant_answers.append(normalized * weight)
        total_weight += weight
    
    if total_weight == 0:
        return 0.0
    
    # Weighted average
    weighted_sum = sum(relevant_answers)
    return weighted_sum / total_weight


def compute_stats(
    seeker_profile_id: UUID,
    session: Session
) -> Dict[str, float]:
    """
    Compute all attribute stats for a seeker
    
    Args:
        seeker_profile_id: UUID of the seeker profile
        session: Database session
    
    Returns:
        Dictionary mapping attribute names to scores (0-100)
    """
    # Load scoring rules to get list of attributes
    scoring_rules = load_scoring_rules()
    attributes = [attr["id"] for attr in scoring_rules["attributes"]]  # Use 'id' not 'name'
    
    # Get all answers for this seeker
    answers_statement = select(Answer).where(Answer.seeker_profile_id == seeker_profile_id)
    answers = session.exec(answers_statement).all()
    
    if not answers:
        # Return zeros if no answers
        return {attr: 0.0 for attr in attributes}
    
    # Get all questions to build lookup dict
    question_ids = [answer.question_id for answer in answers]
    questions_statement = select(Question).where(Question.id.in_(question_ids))
    questions_list = session.exec(questions_statement).all()
    questions_dict = {q.id: q for q in questions_list}
    
    # Compute score for each attribute
    stats = {}
    for attribute in attributes:
        score = compute_attribute_score(answers, questions_dict, attribute)
        stats[attribute] = round(score, 2)
    
    return stats


def compute_fit_score(
    stats: Dict[str, float],
    role_config: OffererRoleConfig
) -> float:
    """
    Compute fit score for a specific role using role-specific weights
    
    Args:
        stats: Dictionary of attribute scores (0-100)
        role_config: Role configuration with weights
    
    Returns:
        Weighted fit score (0-100)
    """
    if not role_config.weights:
        return 0.0
    
    weighted_sum = 0.0
    total_weight = 0.0
    
    for attribute, weight in role_config.weights.items():
        if attribute in stats:
            weighted_sum += stats[attribute] * weight
            total_weight += weight
    
    if total_weight == 0:
        return 0.0
    
    # Weighted average
    fit_score = weighted_sum / total_weight
    return round(fit_score, 2)


def compute_all_fit_scores(
    stats: Dict[str, float],
    session: Session
) -> Dict[str, float]:
    """
    Compute fit scores for all available role configurations
    
    Args:
        stats: Dictionary of attribute scores (0-100)
        session: Database session
    
    Returns:
        Dictionary mapping role names to fit scores (0-100)
    """
    # Get all role configs
    role_configs_statement = select(OffererRoleConfig)
    role_configs = session.exec(role_configs_statement).all()
    
    fit_scores = {}
    for role_config in role_configs:
        fit_score = compute_fit_score(stats, role_config)
        fit_scores[role_config.role_name] = fit_score
    
    return fit_scores
