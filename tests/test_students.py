"""Student CRUD, pagination, validation, and authorization tests."""

from datetime import timedelta

from fastapi.testclient import TestClient

from security import create_access_token


def _create_student(
    client: TestClient,
    headers: dict[str, str],
    **overrides,
):
    payload = {
        "name": "Ada Lovelace",
        "age": 20,
        "course": "Computer Science",
        "email": "ada@example.com",
    }
    payload.update(overrides)
    return client.post("/students", json=payload, headers=headers)


def test_create_student(
    client: TestClient,
    auth_headers: dict[str, str],
    student_payload: dict[str, object],
):
    response = client.post(
        "/students",
        json=student_payload,
        headers=auth_headers,
    )

    assert response.status_code == 201
    body = response.json()
    assert body["message"] == "Student added successfully"
    assert body["student"]["email"] == student_payload["email"]
    assert body["student"]["course"] == student_payload["course"]
    assert isinstance(body["student"]["id"], int)


def test_duplicate_student_email_is_rejected(
    client: TestClient,
    auth_headers: dict[str, str],
    student_payload: dict[str, object],
):
    first = client.post(
        "/students", json=student_payload, headers=auth_headers
    )
    second = client.post(
        "/students",
        json={**student_payload, "email": "ADA@example.com"},
        headers=auth_headers,
    )

    assert first.status_code == 201
    assert second.status_code == 409
    assert second.json()["detail"] == "Student with this email already exists"


def test_list_students_is_paginated(
    client: TestClient,
    auth_headers: dict[str, str],
):
    for index in range(3):
        response = _create_student(
            client,
            auth_headers,
            name=f"Student {index}",
            email=f"student{index}@example.com",
        )
        assert response.status_code == 201, response.text

    first_page = client.get(
        "/students?page=1&page_size=2",
        headers=auth_headers,
    )
    second_page = client.get(
        "/students?page=2&page_size=2",
        headers=auth_headers,
    )

    assert first_page.status_code == 200
    assert first_page.json()["total"] == 3
    assert first_page.json()["pages"] == 2
    assert first_page.json()["page"] == 1
    assert first_page.json()["page_size"] == 2
    assert len(first_page.json()["students"]) == 2

    assert second_page.status_code == 200
    assert len(second_page.json()["students"]) == 1


def test_list_students_rejects_invalid_pagination(
    client: TestClient,
    auth_headers: dict[str, str],
):
    assert (
        client.get("/students?page=0", headers=auth_headers).status_code
        == 422
    )
    assert (
        client.get("/students?page_size=0", headers=auth_headers).status_code
        == 422
    )
    assert (
        client.get("/students?page_size=101", headers=auth_headers).status_code
        == 422
    )


def test_get_student_by_id(
    client: TestClient,
    auth_headers: dict[str, str],
    student_payload: dict[str, object],
):
    created = client.post(
        "/students", json=student_payload, headers=auth_headers
    ).json()["student"]

    response = client.get(
        f"/students/{created['id']}",
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert response.json()["id"] == created["id"]
    assert response.json()["name"] == student_payload["name"]


def test_get_missing_student_returns_404(
    client: TestClient,
    auth_headers: dict[str, str],
):
    response = client.get("/students/999999", headers=auth_headers)

    assert response.status_code == 404
    assert response.json()["detail"] == "Student not found"


def test_update_student(
    client: TestClient,
    auth_headers: dict[str, str],
    student_payload: dict[str, object],
):
    created = client.post(
        "/students", json=student_payload, headers=auth_headers
    ).json()["student"]

    response = client.put(
        f"/students/{created['id']}",
        json={
            "name": "Ada Byron",
            "age": 21,
            "course": "Mathematics",
            "email": "ada.byron@example.com",
        },
        headers=auth_headers,
    )

    assert response.status_code == 200
    body = response.json()
    assert body["message"] == "Student updated successfully"
    assert body["student"]["name"] == "Ada Byron"
    assert body["student"]["course"] == "Mathematics"
    assert body["student"]["email"] == "ada.byron@example.com"


def test_update_to_duplicate_email_is_rejected(
    client: TestClient,
    auth_headers: dict[str, str],
):
    first = _create_student(
        client, auth_headers, email="first@example.com"
    ).json()["student"]
    second = _create_student(
        client,
        auth_headers,
        name="Grace Hopper",
        email="second@example.com",
    ).json()["student"]

    response = client.put(
        f"/students/{second['id']}",
        json={
            "name": "Grace Hopper",
            "age": 30,
            "course": "Computer Science",
            "email": first["email"],
        },
        headers=auth_headers,
    )

    assert response.status_code == 409
    assert response.json()["detail"] == (
        "Email already belongs to another student"
    )


def test_update_missing_student_returns_404(
    client: TestClient,
    auth_headers: dict[str, str],
    student_payload: dict[str, object],
):
    response = client.put(
        "/students/999999",
        json=student_payload,
        headers=auth_headers,
    )

    assert response.status_code == 404


def test_delete_student(
    client: TestClient,
    auth_headers: dict[str, str],
    student_payload: dict[str, object],
):
    created = client.post(
        "/students", json=student_payload, headers=auth_headers
    ).json()["student"]

    response = client.delete(
        f"/students/{created['id']}",
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Student deleted successfully"
    assert response.json()["student"]["id"] == created["id"]

    follow_up = client.get(
        f"/students/{created['id']}",
        headers=auth_headers,
    )
    assert follow_up.status_code == 404


def test_delete_missing_student_returns_404(
    client: TestClient,
    auth_headers: dict[str, str],
):
    response = client.delete("/students/999999", headers=auth_headers)

    assert response.status_code == 404


def test_invalid_student_input_is_rejected(
    client: TestClient,
    auth_headers: dict[str, str],
):
    invalid_payloads = [
        {
            "name": "A",
            "age": 20,
            "course": "Computer Science",
            "email": "a@example.com",
        },
        {
            "name": "Valid Name",
            "age": 0,
            "course": "Computer Science",
            "email": "b@example.com",
        },
        {
            "name": "Valid Name",
            "age": 20,
            "course": "",
            "email": "c@example.com",
        },
        {
            "name": "Valid Name",
            "age": 20,
            "course": "Computer Science",
            "email": "not-an-email",
        },
        {
            "name": "Valid Name",
            "age": 20,
            "email": "missing-course@example.com",
        },
    ]

    for payload in invalid_payloads:
        response = client.post(
            "/students",
            json=payload,
            headers=auth_headers,
        )
        assert response.status_code == 422, payload


def test_student_create_requires_authentication(
    client: TestClient,
    student_payload: dict[str, object],
):
    response = client.post("/students", json=student_payload)

    assert response.status_code == 401


def test_expired_token_is_rejected(
    client: TestClient,
    auth_headers: dict[str, str],
):
    user = client.get("/auth/me", headers=auth_headers).json()
    expired_token = create_access_token(
        subject=user["id"],
        expires_delta=timedelta(seconds=-1),
    )

    response = client.get(
        "/students",
        headers={"Authorization": f"Bearer {expired_token}"},
    )

    assert response.status_code == 401


def test_token_for_unknown_user_is_rejected(client: TestClient):
    token = create_access_token(subject=999999)

    response = client.get(
        "/students",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 401
