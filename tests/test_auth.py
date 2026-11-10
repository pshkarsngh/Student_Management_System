"""Authentication endpoint tests."""

from fastapi.testclient import TestClient


def test_signup_success(client: TestClient):
    response = client.post(
        "/auth/signup",
        json={
            "email": "New.User@Example.com",
            "password": "StrongPass123!",
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "new.user@example.com"
    assert isinstance(body["id"], int)
    assert "password" not in body
    assert "hashed_password" not in body


def test_duplicate_signup_is_rejected(client: TestClient):
    payload = {
        "email": "duplicate@example.com",
        "password": "StrongPass123!",
    }

    first = client.post("/auth/signup", json=payload)
    second = client.post(
        "/auth/signup",
        json={**payload, "email": "DUPLICATE@example.com"},
    )

    assert first.status_code == 201
    assert second.status_code == 409
    assert second.json()["detail"] == "A user with this email already exists"


def test_signup_rejects_invalid_email(client: TestClient):
    response = client.post(
        "/auth/signup",
        json={"email": "not-an-email", "password": "StrongPass123!"},
    )

    assert response.status_code == 422


def test_signup_rejects_short_password(client: TestClient):
    response = client.post(
        "/auth/signup",
        json={"email": "short@example.com", "password": "short"},
    )

    assert response.status_code == 422


def test_login_success_returns_jwt(
    client: TestClient,
    user_credentials: dict[str, str],
):
    client.post("/auth/signup", json=user_credentials)

    response = client.post(
        "/auth/login",
        data={
            "username": user_credentials["email"],
            "password": user_credentials["password"],
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["expires_in"] == 1800
    assert isinstance(body["access_token"], str)
    assert len(body["access_token"].split(".")) == 3


def test_login_with_incorrect_password_is_rejected(
    client: TestClient,
    user_credentials: dict[str, str],
):
    client.post("/auth/signup", json=user_credentials)

    response = client.post(
        "/auth/login",
        data={
            "username": user_credentials["email"],
            "password": "WrongPass123!",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password"
    assert response.headers["www-authenticate"] == "Bearer"


def test_login_with_unknown_email_is_rejected(client: TestClient):
    response = client.post(
        "/auth/login",
        data={"username": "missing@example.com", "password": "StrongPass123!"},
    )

    assert response.status_code == 401


def test_me_returns_current_user(
    client: TestClient,
    auth_headers: dict[str, str],
):
    response = client.get("/auth/me", headers=auth_headers)

    assert response.status_code == 200
    body = response.json()
    assert body["email"] == "manager@example.com"
    assert "hashed_password" not in body


def test_me_requires_a_token(client: TestClient):
    response = client.get("/auth/me")

    assert response.status_code == 401


def test_me_rejects_invalid_token(client: TestClient):
    response = client.get(
        "/auth/me",
        headers={"Authorization": "Bearer not-a-real-token"},
    )

    assert response.status_code == 401


def test_protected_route_requires_authentication(client: TestClient):
    response = client.get("/students")

    assert response.status_code == 401
