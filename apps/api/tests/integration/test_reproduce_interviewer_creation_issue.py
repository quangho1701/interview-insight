"""Reproduction script for interviewer creation issue."""
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session
from app.core.security import create_access_token, get_password_hash
from app.models.enums import AuthProvider
from app.models.user import User

@pytest.fixture
def test_user(db_session: Session) -> User:
    """Create a test user for interviewer tests."""
    user = User(
        email="repro_test@example.com",
        provider=AuthProvider.LOCAL,
        hashed_password=get_password_hash("testpassword123"),
        credits=10,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def auth_headers(test_user: User) -> dict:
    """Create authorization headers for test user."""
    token = create_access_token(subject=str(test_user.id))
    return {"Authorization": f"Bearer {token}"}

def test_create_interviewer_without_company(
    client: TestClient, auth_headers: dict
):
    """Attempt to create an interviewer without a company."""
    print("\nAttempting to create interviewer with just name...")
    # Intentionally sending only name, no company field at all
    response = client.post(
        "/api/v1/interviewers",
        json={"name": "Test Interviewer Only Name"},
        headers=auth_headers,
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Interviewer Only Name"
    # company should be None
    assert data.get("company") is None

def test_create_interviewer_with_empty_string_company(
    client: TestClient, auth_headers: dict
):
    """Attempt to create an interviewer with empty string company."""
    print("\nAttempting to create interviewer with empty string company...")
    response = client.post(
        "/api/v1/interviewers",
        json={"name": "Test Interviewer Empty Company", "company": ""},
        headers=auth_headers,
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Interviewer Empty Company"
    assert data["company"] == ""
