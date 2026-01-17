"""Pytest fixtures for VibeCheck API tests."""

import os
from typing import Generator

import pytest
from sqlmodel import Session, SQLModel, create_engine

# Set test environment variables before importing app modules
os.environ.setdefault("DATABASE_HOST", "localhost")
os.environ.setdefault("DATABASE_PORT", "5433")  # Test DB port
os.environ.setdefault("DATABASE_USER", "postgres")
os.environ.setdefault("DATABASE_PASSWORD", "postgres")
os.environ.setdefault("DATABASE_NAME", "vibecheck_test")
os.environ.setdefault("REDIS_HOST", "localhost")
os.environ.setdefault("REDIS_PORT", "6380")  # Test Redis port


@pytest.fixture(scope="session")
def test_engine():
    """Create test database engine."""
    from app.core.config import get_settings

    settings = get_settings()
    engine = create_engine(
        settings.database_url,
        echo=False,
    )
    return engine


@pytest.fixture(scope="session")
def setup_database(test_engine):
    """Create all tables before tests, drop after."""
    # Import all models to register them with SQLModel
    from app.models import (  # noqa: F401
        InterviewAnalysis,
        Interviewer,
        ProcessingJob,
        User,
    )

    SQLModel.metadata.create_all(test_engine)
    yield
    SQLModel.metadata.drop_all(test_engine)


@pytest.fixture
def db_session(test_engine, setup_database) -> Generator[Session, None, None]:
    """Provide a transactional database session for tests."""
    with Session(test_engine) as session:
        yield session
        # Rollback any uncommitted changes
        session.rollback()
