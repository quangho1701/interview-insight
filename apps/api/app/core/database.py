"""Database configuration and session management."""

from functools import lru_cache
from typing import Generator

from sqlmodel import Session, SQLModel, create_engine

from app.core.config import get_settings


@lru_cache
def get_engine():
    """Create and cache database engine with connection pooling."""
    settings = get_settings()
    engine = create_engine(
        settings.database_url,
        echo=settings.debug,
        pool_size=5,
        max_overflow=10,
        pool_recycle=3600,
        pool_pre_ping=True,
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
