"""Shared pytest fixtures.

Environment variables are set BEFORE importing the application so the test
suite uses an isolated in-memory SQLite database instead of PostgreSQL.
"""

import os

os.environ["DATABASE_URL"] = "sqlite+pysqlite:///:memory:"
os.environ["JWT_SECRET_KEY"] = (
    "test-only-jwt-secret-key-with-more-than-32-characters"
)
os.environ["JWT_ALGORITHM"] = "HS256"
os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "30"

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from database import Base, engine  # noqa: E402
from main import app  # noqa: E402


@pytest.fixture()
def client():
    """Provide a TestClient backed by a clean in-memory database."""

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    with TestClient(app) as test_client:
        yield test_client

    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def user_credentials() -> dict[str, str]:
    return {
        "email": "manager@example.com",
        "password": "StrongPass123!",
    }


@pytest.fixture()
def auth_headers(
    client: TestClient,
    user_credentials: dict[str, str],
) -> dict[str, str]:
    """Create a user, log in, and return a bearer auth header."""

    signup = client.post("/auth/signup", json=user_credentials)
    assert signup.status_code == 201, signup.text

    login = client.post(
        "/auth/login",
        data={
            "username": user_credentials["email"],
            "password": user_credentials["password"],
        },
    )
    assert login.status_code == 200, login.text

    token = login.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def student_payload() -> dict[str, object]:
    return {
        "name": "Ada Lovelace",
        "age": 20,
        "course": "Computer Science",
        "email": "ada@example.com",
    }
