"""
Unit tests for scoring service
"""
import pytest
from uuid import uuid4
from services.scoring import (
    normalize_score,
    compute_attribute_score,
    compute_fit_score,
    load_scoring_rules
)
from models import Question, Answer, OffererRoleConfig
from models.questionnaire import QuestionType


def test_normalize_score():
    """Test score normalization to 0-100 scale"""
    # Test with default range 0-5
    assert normalize_score(0, 0, 5) == 0.0
    assert normalize_score(2.5, 0, 5) == 50.0
    assert normalize_score(5, 0, 5) == 100.0
    
    # Test with custom range 1-10
    assert normalize_score(1, 1, 10) == 0.0
    assert normalize_score(5.5, 1, 10) == 50.0
    assert normalize_score(10, 1, 10) == 100.0
    
    # Test clamping
    assert normalize_score(-1, 0, 5) == 0.0
    assert normalize_score(10, 0, 5) == 100.0


def test_compute_attribute_score_single_question():
    """Test computing attribute score from a single question"""
    # Create mock question
    question_id = uuid4()
    question = Question(
        id=question_id,
        questionnaire_id=uuid4(),
        text="Rate your Python skills",
        question_type=QuestionType.SCALE,
        order=1,
        options={"min": 1, "max": 5},
        scoring_config={"attribute": "technical_skills", "weight": 1.0}
    )
    
    # Create mock answer with value 4 (out of 1-5 scale)
    answer = Answer(
        id=uuid4(),
        seeker_profile_id=uuid4(),
        question_id=question_id,
        answer_value={"value": 4}
    )
    
    questions_dict = {question_id: question}
    score = compute_attribute_score([answer], questions_dict, "technical_skills")
    
    # 4 on a 1-5 scale = 75% of range = 75.0
    # (4-1)/(5-1) * 100 = 3/4 * 100 = 75.0
    assert score == 75.0


def test_compute_attribute_score_multiple_questions():
    """Test computing attribute score from multiple questions with weights"""
    # Create two questions for same attribute
    q1_id = uuid4()
    q2_id = uuid4()
    questionnaire_id = uuid4()
    
    q1 = Question(
        id=q1_id,
        questionnaire_id=questionnaire_id,
        text="Python skills",
        question_type=QuestionType.SCALE,
        order=1,
        options={"min": 1, "max": 5},
        scoring_config={"attribute": "technical_skills", "weight": 2.0}  # Double weight
    )
    
    q2 = Question(
        id=q2_id,
        questionnaire_id=questionnaire_id,
        text="JavaScript skills",
        question_type=QuestionType.SCALE,
        order=2,
        options={"min": 1, "max": 5},
        scoring_config={"attribute": "technical_skills", "weight": 1.0}
    )
    
    # Answers: q1=5 (100%), q2=3 (50%)
    a1 = Answer(
        id=uuid4(),
        seeker_profile_id=uuid4(),
        question_id=q1_id,
        answer_value={"value": 5}
    )
    
    a2 = Answer(
        id=uuid4(),
        seeker_profile_id=uuid4(),
        question_id=q2_id,
        answer_value={"value": 3}
    )
    
    questions_dict = {q1_id: q1, q2_id: q2}
    score = compute_attribute_score([a1, a2], questions_dict, "technical_skills")
    
    # q1: (5-1)/(5-1) * 100 = 100.0, weight=2.0 -> 200.0
    # q2: (3-1)/(5-1) * 100 = 50.0, weight=1.0 -> 50.0
    # Weighted avg: (200.0 + 50.0) / (2.0 + 1.0) = 250.0 / 3.0 = 83.33
    assert round(score, 2) == 83.33


def test_compute_attribute_score_ignores_other_attributes():
    """Test that scoring only includes questions for the target attribute"""
    q1_id = uuid4()
    q2_id = uuid4()
    questionnaire_id = uuid4()
    
    # Technical skills question
    q1 = Question(
        id=q1_id,
        questionnaire_id=questionnaire_id,
        text="Python skills",
        question_type=QuestionType.SCALE,
        order=1,
        options={"min": 1, "max": 5},
        scoring_config={"attribute": "technical_skills", "weight": 1.0}
    )
    
    # Communication question - should be ignored
    q2 = Question(
        id=q2_id,
        questionnaire_id=questionnaire_id,
        text="Presentation skills",
        question_type=QuestionType.SCALE,
        order=2,
        options={"min": 1, "max": 5},
        scoring_config={"attribute": "communication", "weight": 1.0}
    )
    
    a1 = Answer(id=uuid4(), seeker_profile_id=uuid4(), question_id=q1_id, answer_value={"value": 4})
    a2 = Answer(id=uuid4(), seeker_profile_id=uuid4(), question_id=q2_id, answer_value={"value": 2})
    
    questions_dict = {q1_id: q1, q2_id: q2}
    score = compute_attribute_score([a1, a2], questions_dict, "technical_skills")
    
    # Only q1 counts: (4-1)/(5-1) * 100 = 75.0
    assert score == 75.0


def test_compute_fit_score():
    """Test computing role fit score using weights"""
    # Create role config with weights
    role_config = OffererRoleConfig(
        id=uuid4(),
        role_name="Software Engineer",
        weights={
            "technical_skills": 0.5,  # 50% weight
            "problem_solving": 0.3,   # 30% weight
            "communication": 0.2       # 20% weight
        }
    )
    
    # Mock stats
    stats = {
        "technical_skills": 90.0,
        "problem_solving": 80.0,
        "communication": 70.0,
        "leadership": 60.0,  # Not in weights, should be ignored
    }
    
    fit_score = compute_fit_score(stats, role_config)
    
    # (90*0.5 + 80*0.3 + 70*0.2) / (0.5 + 0.3 + 0.2)
    # (45 + 24 + 14) / 1.0 = 83.0
    assert fit_score == 83.0


def test_compute_fit_score_with_missing_stats():
    """Test fit score computation when some stats are missing"""
    role_config = OffererRoleConfig(
        id=uuid4(),
        role_name="Test Role",
        weights={
            "technical_skills": 0.6,
            "communication": 0.4
        }
    )
    
    # Only technical_skills present
    stats = {
        "technical_skills": 80.0
    }
    
    fit_score = compute_fit_score(stats, role_config)
    
    # Only technical_skills counts: (80*0.6) / 0.6 = 80.0
    assert fit_score == 80.0


def test_load_scoring_rules():
    """Test loading scoring rules from JSON file"""
    rules = load_scoring_rules()
    
    assert "attributes" in rules
    assert isinstance(rules["attributes"], list)
    assert len(rules["attributes"]) == 6
    
    # Check that standard attributes exist
    attribute_names = [attr["id"] for attr in rules["attributes"]]
    assert "technical_skills" in attribute_names
    assert "communication" in attribute_names
    assert "leadership" in attribute_names
    assert "problem_solving" in attribute_names
    assert "adaptability" in attribute_names
    assert "teamwork" in attribute_names


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])
