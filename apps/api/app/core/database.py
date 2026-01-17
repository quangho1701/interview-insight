"""Database configuration and session management."""

from typing import Generator

from sqlmodel import Session, SQLModel, create_engine

from app.core.config import get_settings


def get_engine():
    """Create database engine."""
    settings = get_settings()
    engine = create_engine(
        settings.database_url,
        echo=settings.debug,
    )
    return engine


def create_db_and_tables():
    """Create all database tables."""
    engine = get_engine()
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """Get database session for dependency injection."""
    engine = get_engine()
    with Session(engine) as session:
        yield session
