"""
Seed database with initial data
- Creates questionnaire with questions
- Creates offerer role configurations
- Idempotent: safe to run multiple times
"""
import json
import sys
from pathlib import Path
from uuid import UUID, uuid4

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from sqlmodel import Session, select
from database import engine
from models import (
    Questionnaire,
    Question,
    QuestionType,
    OffererRoleConfig,
)


def load_scoring_rules():
    """Load scoring rules from shared package"""
    rules_path = Path(__file__).parent.parent.parent / "packages" / "shared" / "scoring-rules.json"
    with open(rules_path, "r") as f:
        return json.load(f)


def seed_questionnaire(session: Session):
    """Create or update the main questionnaire with questions"""
    
    # Check if questionnaire already exists
    stmt = select(Questionnaire).where(Questionnaire.name == "General Skills Assessment")
    existing = session.exec(stmt).first()
    
    if existing:
        print(f"✓ Questionnaire '{existing.name}' already exists (ID: {existing.id})")
        questionnaire_id = existing.id
    else:
        # Create questionnaire
        questionnaire = Questionnaire(
            id=uuid4(),
            name="General Skills Assessment",
            description="Comprehensive assessment of professional skills and attributes",
            version=1,
            is_active=True
        )
        session.add(questionnaire)
        session.commit()
        session.refresh(questionnaire)
        questionnaire_id = questionnaire.id
        print(f"✓ Created questionnaire: {questionnaire.name}")
    
    # Define questions
    questions_data = [
        {
            "text": "Rate your proficiency with programming languages and technical tools",
            "type": QuestionType.SCALE,
            "order": 1,
            "options": {"min": 1, "max": 10, "labels": {"1": "Beginner", "10": "Expert"}},
            "scoring": {"attribute": "technical_skills", "weight": 0.4}
        },
        {
            "text": "How comfortable are you debugging complex technical issues?",
            "type": QuestionType.SCALE,
            "order": 2,
            "options": {"min": 1, "max": 10},
            "scoring": {"attribute": "technical_skills", "weight": 0.3}
        },
        {
            "text": "Rate your ability to learn and adapt to new technologies",
            "type": QuestionType.SCALE,
            "order": 3,
            "options": {"min": 1, "max": 10},
            "scoring": {"attribute": "technical_skills", "weight": 0.3}
        },
        {
            "text": "How effectively can you explain technical concepts to non-technical people?",
            "type": QuestionType.SCALE,
            "order": 4,
            "options": {"min": 1, "max": 10},
            "scoring": {"attribute": "communication", "weight": 0.4}
        },
        {
            "text": "Rate your written communication skills (emails, documentation, reports)",
            "type": QuestionType.SCALE,
            "order": 5,
            "options": {"min": 1, "max": 10},
            "scoring": {"attribute": "communication", "weight": 0.3}
        },
        {
            "text": "How comfortable are you presenting to groups?",
            "type": QuestionType.SCALE,
            "order": 6,
            "options": {"min": 1, "max": 10},
            "scoring": {"attribute": "communication", "weight": 0.3}
        },
        {
            "text": "Have you led a team or project?",
            "type": QuestionType.YES_NO,
            "order": 7,
            "options": {},
            "scoring": {"attribute": "leadership", "weight": 0.3}
        },
        {
            "text": "Rate your ability to make decisions under pressure",
            "type": QuestionType.SCALE,
            "order": 8,
            "options": {"min": 1, "max": 10},
            "scoring": {"attribute": "leadership", "weight": 0.4}
        },
        {
            "text": "How well do you mentor or guide others?",
            "type": QuestionType.SCALE,
            "order": 9,
            "options": {"min": 1, "max": 10},
            "scoring": {"attribute": "leadership", "weight": 0.3}
        },
        {
            "text": "Rate your analytical and problem-solving abilities",
            "type": QuestionType.SCALE,
            "order": 10,
            "options": {"min": 1, "max": 10},
            "scoring": {"attribute": "problem_solving", "weight": 0.5}
        },
        {
            "text": "How do you approach complex, ambiguous problems?",
            "type": QuestionType.MULTIPLE_CHOICE,
            "order": 11,
            "options": {
                "choices": [
                    {"value": "break_down", "label": "Break them into smaller parts", "score": 9},
                    {"value": "research", "label": "Research similar solutions", "score": 7},
                    {"value": "collaborate", "label": "Collaborate with others", "score": 8},
                    {"value": "trial_error", "label": "Trial and error", "score": 5}
                ]
            },
            "scoring": {"attribute": "problem_solving", "weight": 0.5}
        },
        {
            "text": "How quickly do you adapt to change?",
            "type": QuestionType.SCALE,
            "order": 12,
            "options": {"min": 1, "max": 10},
            "scoring": {"attribute": "adaptability", "weight": 0.5}
        },
        {
            "text": "Rate your comfort with ambiguity and uncertainty",
            "type": QuestionType.SCALE,
            "order": 13,
            "options": {"min": 1, "max": 10},
            "scoring": {"attribute": "adaptability", "weight": 0.5}
        },
        {
            "text": "How well do you work in a team environment?",
            "type": QuestionType.SCALE,
            "order": 14,
            "options": {"min": 1, "max": 10},
            "scoring": {"attribute": "teamwork", "weight": 0.4}
        },
        {
            "text": "Rate your ability to handle conflicts within a team",
            "type": QuestionType.SCALE,
            "order": 15,
            "options": {"min": 1, "max": 10},
            "scoring": {"attribute": "teamwork", "weight": 0.3}
        },
        {
            "text": "How do you contribute to team success?",
            "type": QuestionType.MULTIPLE_CHOICE,
            "order": 16,
            "options": {
                "choices": [
                    {"value": "lead", "label": "Take leadership roles", "score": 8},
                    {"value": "support", "label": "Support team members", "score": 9},
                    {"value": "execute", "label": "Execute tasks efficiently", "score": 7},
                    {"value": "innovate", "label": "Bring new ideas", "score": 8}
                ]
            },
            "scoring": {"attribute": "teamwork", "weight": 0.3}
        },
    ]
    
    # Check existing questions for this questionnaire
    stmt = select(Question).where(Question.questionnaire_id == questionnaire_id)
    existing_questions = session.exec(stmt).all()
    
    if existing_questions:
        print(f"✓ Questionnaire already has {len(existing_questions)} questions")
    else:
        # Create questions
        for q_data in questions_data:
            question = Question(
                id=uuid4(),
                questionnaire_id=questionnaire_id,
                text=q_data["text"],
                question_type=q_data["type"],
                order=q_data["order"],
                options=q_data["options"],
                scoring_config=q_data["scoring"],
                is_active=True
            )
            session.add(question)
        
        session.commit()
        print(f"✓ Created {len(questions_data)} questions")


def seed_role_configs(session: Session):
    """Create offerer role configurations"""
    
    role_configs = [
        {
            "role_name": "Software Engineer",
            "description": "Technical role focused on coding, architecture, and problem-solving",
            "weights": {
                "technical_skills": 0.40,
                "problem_solving": 0.30,
                "communication": 0.15,
                "teamwork": 0.10,
                "leadership": 0.03,
                "adaptability": 0.02
            },
            "display_config": {
                "primary_attributes": ["technical_skills", "problem_solving"],
                "card_color": "#3b82f6"
            }
        },
        {
            "role_name": "Sales Representative",
            "description": "Client-facing role focused on communication and relationship building",
            "weights": {
                "communication": 0.40,
                "adaptability": 0.25,
                "problem_solving": 0.15,
                "teamwork": 0.10,
                "leadership": 0.05,
                "technical_skills": 0.05
            },
            "display_config": {
                "primary_attributes": ["communication", "adaptability"],
                "card_color": "#10b981"
            }
        },
        {
            "role_name": "Team Lead",
            "description": "Management role focused on leadership and team coordination",
            "weights": {
                "leadership": 0.35,
                "communication": 0.25,
                "problem_solving": 0.20,
                "teamwork": 0.10,
                "adaptability": 0.05,
                "technical_skills": 0.05
            },
            "display_config": {
                "primary_attributes": ["leadership", "communication"],
                "card_color": "#f59e0b"
            }
        }
    ]
    
    for role_data in role_configs:
        # Check if role config exists
        stmt = select(OffererRoleConfig).where(OffererRoleConfig.role_name == role_data["role_name"])
        existing = session.exec(stmt).first()
        
        if existing:
            print(f"✓ Role config '{role_data['role_name']}' already exists")
        else:
            role_config = OffererRoleConfig(
                id=uuid4(),
                role_name=role_data["role_name"],
                description=role_data["description"],
                weights=role_data["weights"],
                display_config=role_data["display_config"],
                is_active=True
            )
            session.add(role_config)
            session.commit()
            print(f"✓ Created role config: {role_data['role_name']}")


def main():
    """Run all seed operations"""
    print("🌱 Starting database seeding...")
    print()
    
    # Load scoring rules (validate they exist)
    try:
        scoring_rules = load_scoring_rules()
        print(f"✓ Loaded scoring rules: {len(scoring_rules['attributes'])} attributes defined")
        print()
    except Exception as e:
        print(f"❌ Failed to load scoring rules: {e}")
        sys.exit(1)
    
    with Session(engine) as session:
        try:
            seed_questionnaire(session)
            print()
            seed_role_configs(session)
            print()
            print("✅ Database seeding completed successfully!")
            
        except Exception as e:
            print(f"\n❌ Error during seeding: {e}")
            session.rollback()
            raise


if __name__ == "__main__":
    main()
