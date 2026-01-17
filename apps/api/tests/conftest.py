"""Pytest fixtures for VibeCheck API tests."""

import os
from typing import Generator

import pytest
from sqlalchemy import event
from sqlmodel import Session, SQLModel, create_engine

# Set test environment variables before importing app modules
os.environ.setdefault("DATABASE_HOST", "localhost")
os.environ.setdefault("DATABASE_PORT", "5433")  # Test DB port
os.environ.setdefault("DATABASE_USER", "postgres")
os.environ.setdefault("DATABASE_PASSWORD", "postgres")
os.environ.setdefault("DATABASE_NAME", "vibecheck_test")
os.environ.setdefault("REDIS_HOST", "localhost")
os.environ.setdefault("REDIS_PORT", "6380")  # Test Redis port
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-testing-only")

from fastapi.testclient import TestClient


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
    """Provide a transactional database session for tests.

    Uses a nested transaction (SAVEPOINT) so that commits within the test
    can be rolled back at the end.
    """
    connection = test_engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)

    # Begin a nested transaction (savepoint)
    nested = connection.begin_nested()

    # If the session commits, restart the nested transaction
    @event.listens_for(session, "after_transaction_end")
    def restart_savepoint(session, trans):
        nonlocal nested
        if trans.nested and not trans._parent.nested:
            nested = connection.begin_nested()

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db_session, setup_database) -> Generator[TestClient, None, None]:
    """Provide a test client with database session override.

    Shares the same session as db_session fixture for proper transaction isolation.
    """
    from app.core.database import get_session
    from app.main import app

    def get_test_session() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_session] = get_test_session
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
