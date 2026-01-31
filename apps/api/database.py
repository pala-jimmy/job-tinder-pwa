"""
Database configuration and session management
"""
from typing import Generator
from sqlmodel import SQLModel, Session, create_engine
from config import get_settings

settings = get_settings()

# Create engine
# SQLite needs check_same_thread=False for FastAPI
connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
engine = create_engine(
    settings.database_url,
    echo=settings.debug,
    connect_args=connect_args
)


def create_db_and_tables():
    """Create all database tables"""
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """
    Dependency for getting database sessions
    Usage: session: Session = Depends(get_session)
    """
    with Session(engine) as session:
        yield session
