<div align="center">

# Student Management System API

**A secure, portfolio-grade backend for managing student records.**

Built with FastAPI, PostgreSQL, SQLAlchemy, Pydantic, Argon2, and JWT authentication.

[![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.162.x-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-4169E1?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.x-D71F00?logo=sqlalchemy&logoColor=white)](https://www.sqlalchemy.org/)
[![JWT](https://img.shields.io/badge/Auth-JWT-000000?logo=jsonwebtokens&logoColor=white)](https://jwt.io/)
[![Tests](https://img.shields.io/badge/Tests-36%20passing-brightgreen)](#testing)

</div>

---

## Overview

This project is a complete **Student Management System backend** designed to
demonstrate clean API architecture, secure authentication, validated request
contracts, safe database access, and automated testing.

Authenticated users can create, list, view, update, and delete student records.
Student routes are protected with bearer JWTs, passwords are hashed with Argon2,
and secrets are loaded exclusively from environment variables.

> **Visual documentation:** GitHub renders the Mermaid diagrams in this README
> automatically.

---

## Table of Contents

- [Overview](#overview)
- [Highlights](#highlights)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Configuration](#configuration)
- [Database Setup](#database-setup)
- [Running the API](#running-the-api)
- [Authentication](#authentication)
- [API Reference](#api-reference)
- [Error Handling](#error-handling)
- [Security](#security)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)
- [Production Hardening](#production-hardening)
- [Author](#author)

---

## Highlights

| Area | Capability |
| --- | --- |
| Authentication | Signup, login, JWT access tokens, current-user endpoint |
| Password security | Argon2 hashing with secure verification |
| Authorization | Bearer-token protection on every student route |
| Student management | Full CRUD with duplicate-email protection |
| API quality | Typed request/response schemas and pagination |
| Reliability | Rollback-safe database sessions and controlled errors |
| Configuration | Environment-based secrets with startup validation |
| Testing | 36 automated tests with FastAPI `TestClient` |
| Documentation | Swagger UI, ReDoc, OpenAPI, and Mermaid diagrams |

### Architecture decisions

- **Routers by domain** — authentication and student endpoints are isolated in
  `routers/auth.py` and `routers/students.py`.
- **Authentication as a dependency** — `dependencies.py` centralizes JWT
  validation and current-user resolution.
- **Security primitives separated** — Argon2 and JWT logic live in
  `security.py`, independent of HTTP routing.
- **Schemas separate from ORM models** — `schemas.py` defines the public API
  contract and never exposes hashed passwords.
- **Explicit configuration** — `config.py` validates required environment
  variables at startup.
- **Isolated tests** — the suite uses in-memory SQLite and never touches
  PostgreSQL data.

---

## Architecture

### System graph

```mermaid
flowchart LR
    Browser["Swagger UI / HTTP client"]

    subgraph API["FastAPI application"]
        Main["main.py<br/>lifespan + routers"]
        AuthRouter["routers/auth.py"]
        StudentRouter["routers/students.py"]
        Deps["dependencies.py<br/>get_current_user"]
        Schemas["schemas.py<br/>Pydantic validation"]
        Security["security.py<br/>Argon2 + JWT"]
    end

    subgraph Data["Data layer"]
        Models["models.py<br/>SQLAlchemy models"]
        DB[("PostgreSQL")]
    end

    Browser -->|"HTTP / JSON or form"| Main
    Main --> AuthRouter
    Main --> StudentRouter
    AuthRouter --> Schemas
    AuthRouter --> Security
    AuthRouter --> Models
    StudentRouter --> Schemas
    StudentRouter --> Deps
    Deps --> Security
    Deps --> Models
    StudentRouter --> Models
    Models --> DB
```

### Request lifecycle

```mermaid
flowchart TD
    Request["Incoming request"] --> Validate["Pydantic validation"]
    Validate -->|"invalid"| E422["422 Unprocessable Entity"]
    Validate -->|"valid"| AuthCheck{"Valid Bearer JWT?"}
    AuthCheck -->|"no"| E401["401 Unauthorized"]
    AuthCheck -->|"yes"| Handler["Route handler"]
    Handler --> DB[("PostgreSQL")]
    DB -->|"duplicate email"| E409["Rollback + 409 Conflict"]
    DB -->|"other database error"| E500["Rollback + 500 Internal Server Error"]
    DB -->|"success"| Response["Typed response model"]
    Response --> Client["Client receives JSON"]
```

---

## Tech Stack

| Layer | Technology | Purpose |
| --- | --- | --- |
| Language | Python 3.12 | Runtime |
| Web framework | FastAPI | HTTP API, dependency injection, OpenAPI |
| Database | PostgreSQL | Persistent relational storage |
| ORM | SQLAlchemy 2.x | Models, sessions, transactions |
| Validation | Pydantic 2.x | Request/response schemas |
| Settings | pydantic-settings | Typed environment configuration |
| Password hashing | Argon2 via `pwdlib[argon2]` | Secure password storage |
| Authentication | JWT via PyJWT | Stateless access tokens |
| Testing | pytest + FastAPI `TestClient` | Automated API and unit tests |

---

## Project Structure

```text
Student_management_System/
├── main.py                 # FastAPI app, lifespan, router registration
├── config.py               # Typed environment settings and validation
├── database.py             # Engine, session factory, get_db, create_tables
├── models.py               # Student and User SQLAlchemy models
├── schemas.py              # Pydantic request/response schemas
├── security.py             # Argon2 hashing and JWT helpers
├── dependencies.py         # OAuth2 bearer scheme + current-user dependency
├── routers/
│   ├── auth.py             # /auth/signup, /auth/login, /auth/me
│   └── students.py         # Protected /students CRUD + pagination
├── migrations/
│   └── 001_students_course_not_null.sql
├── scripts/
│   ├── check_db.py         # Manual PostgreSQL connectivity check
│   └── check_security.py   # Manual Argon2 hashing check
├── tests/
│   ├── conftest.py
│   ├── test_auth.py
│   ├── test_config.py
│   ├── test_security.py
│   └── test_students.py
├── .env.example            # Placeholder configuration (safe to commit)
├── pytest.ini
├── requirements.txt
└── README.md
```

---

## Getting Started

### Prerequisites

- **Python 3.12+**
- **PostgreSQL** (local or hosted)
- **Git**
- `pip` and a virtual environment

### 1. Clone the repository

```bash
git clone https://github.com/pshkarsngh/Student_Management_System.git
cd Student_Management_System
```

### 2. Create and activate a virtual environment

Windows PowerShell:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

macOS / Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

---

## Configuration

Copy the example environment file and replace the placeholders:

Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

macOS / Linux:

```bash
cp .env.example .env
```

### Environment variables

| Variable | Required | Default | Description |
| --- | --- | --- | --- |
| `DATABASE_URL` | Yes | — | SQLAlchemy PostgreSQL connection URL |
| `JWT_SECRET_KEY` | Yes | — | Secret used to sign JWTs; minimum 32 characters |
| `JWT_ALGORITHM` | No | `HS256` | `HS256`, `HS384`, or `HS512` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | No | `30` | Access-token lifetime in minutes |

Example `.env`:

```env
DATABASE_URL=postgresql://username:password@localhost:5432/student_management
JWT_SECRET_KEY=replace-with-a-long-random-secret-at-least-32-characters
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

Generate a strong JWT secret:

```bash
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

> The application refuses to start if `JWT_SECRET_KEY` is missing, shorter than
> 32 characters, or still set to the example placeholder.

**Never commit `.env`.** Only `.env.example` belongs in version control.

---

## Database Setup

### 1. Create the database

Using `psql`:

```sql
CREATE DATABASE student_management;
```

Or using `createdb`:

```bash
createdb student_management
```

### 2. Create tables

Tables are created automatically on application startup through the FastAPI
lifespan handler:

- `students`
- `users`

### Entity relationship graph

```mermaid
erDiagram
    USERS {
        int id PK
        varchar email UK "unique and indexed"
        varchar hashed_password "Argon2 hash"
    }

    STUDENTS {
        int id PK
        varchar name
        int age
        varchar course "required"
        varchar email UK "unique and indexed"
    }
```

`users` and `students` are intentionally independent tables: any authenticated
user can manage student records, so there is no per-user foreign key.

### Existing database migration

The application requires `students.course` to be `NOT NULL`. Fresh databases get
this automatically. If you are upgrading an older database where `course` is
nullable, apply the safe migration:

```bash
psql "$DATABASE_URL" -f migrations/001_students_course_not_null.sql
```

Windows PowerShell:

```powershell
psql $env:DATABASE_URL -f migrations/001_students_course_not_null.sql
```

The migration does **not** delete or recreate the database or any rows. If a
row contains a `NULL` course, `SET NOT NULL` fails safely and the transaction
rolls back; resolve that row and run the migration again.

### Verify the connection

```bash
python scripts/check_db.py
```

Expected output:

```text
PostgreSQL connected successfully!
```

---

## Running the API

From the project root with the virtual environment active:

```bash
uvicorn main:app --reload
```

Or with the FastAPI CLI:

```bash
fastapi dev main.py
```

The API is available at:

| Resource | URL |
| --- | --- |
| API root | <http://127.0.0.1:8000/> |
| Swagger UI | <http://127.0.0.1:8000/docs> |
| ReDoc | <http://127.0.0.1:8000/redoc> |
| OpenAPI JSON | <http://127.0.0.1:8000/openapi.json> |

For production, omit `--reload` and run the app behind a process manager and
HTTPS reverse proxy.

---

## Authentication

Authentication uses the OAuth2 password flow with bearer JWTs.

### Authentication flow

```mermaid
sequenceDiagram
    autonumber
    participant C as Client
    participant A as FastAPI /auth
    participant S as security.py
    participant DB as PostgreSQL

    C->>A: POST /auth/signup
    A->>DB: Check duplicate email
    A->>S: hash_password(password)
    S-->>A: Argon2 hash
    A->>DB: INSERT user
    A-->>C: 201 Created

    C->>A: POST /auth/login (form data)
    A->>DB: SELECT user by email
    A->>S: verify_password(password, hash)
    S-->>A: true or false
    A->>S: create_access_token(user.id)
    S-->>A: signed JWT
    A-->>C: 200 OK + access_token

    C->>A: GET /students with Bearer token
    A->>S: decode_access_token(token)
    S-->>A: payload or InvalidTokenError
    A->>DB: SELECT user by sub
    A->>DB: SELECT paginated students
    A-->>C: 200 OK + student page
```

### 1. Sign up

```bash
curl -X POST http://127.0.0.1:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"StrongPass123!"}'
```

Response `201 Created`:

```json
{
  "id": 1,
  "email": "user@example.com"
}
```

### 2. Log in

`POST /auth/login` expects `application/x-www-form-urlencoded` data (OAuth2
standard), not JSON:

```bash
curl -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user@example.com&password=StrongPass123!"
```

Response `200 OK`:

```json
{
  "access_token": "<jwt>",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### 3. Authorize requests

Send the token in the `Authorization` header:

```text
Authorization: Bearer <access_token>
```

In Swagger UI, click **Authorize**, enter your email as the username and your
password, and Swagger will attach the token automatically.

### 4. Read the current user

```bash
curl http://127.0.0.1:8000/auth/me \
  -H "Authorization: Bearer <access_token>"
```

---

## API Reference

### Route graph

```mermaid
flowchart TD
    API["Student Management API"] --> Public["Public routes"]
    API --> Protected["Protected routes<br/>Bearer JWT required"]

    Public --> Root["GET /"]
    Public --> Signup["POST /auth/signup"]
    Public --> Login["POST /auth/login"]

    Protected --> Me["GET /auth/me"]
    Protected --> Create["POST /students"]
    Protected --> List["GET /students<br/>page + page_size"]
    Protected --> Read["GET /students/{student_id}"]
    Protected --> Update["PUT /students/{student_id}"]
    Protected --> Delete["DELETE /students/{student_id}"]
```

### Public endpoints

| Method | Endpoint | Description | Success |
| --- | --- | --- | --- |
| `GET` | `/` | Health/landing endpoint | `200` |
| `POST` | `/auth/signup` | Register a user | `201` |
| `POST` | `/auth/login` | Obtain a JWT (form data) | `200` |

### Protected endpoints

Require `Authorization: Bearer <token>`.

| Method | Endpoint | Description | Success |
| --- | --- | --- | --- |
| `GET` | `/auth/me` | Current authenticated user | `200` |
| `POST` | `/students` | Create a student | `201` |
| `GET` | `/students?page=1&page_size=10` | Paginated student list | `200` |
| `GET` | `/students/{student_id}` | Get one student | `200` |
| `PUT` | `/students/{student_id}` | Replace student details | `200` |
| `DELETE` | `/students/{student_id}` | Delete a student | `200` |

### Student request body

```json
{
  "name": "Ada Lovelace",
  "age": 20,
  "course": "Computer Science",
  "email": "ada@example.com"
}
```

### Validation rules

| Field | Rule |
| --- | --- |
| `name` | 2–100 characters, not blank |
| `age` | Integer greater than `0`, at most `120` |
| `course` | 2–100 characters, not blank |
| `email` | Valid email address; stored lowercase |
| `password` | 8–128 characters (signup only) |

### Pagination

`GET /students` accepts:

- `page` — 1-based page number, default `1`, minimum `1`.
- `page_size` — records per page, default `10`, range `1`–`100`.

Response:

```json
{
  "students": [
    {
      "id": 1,
      "name": "Ada Lovelace",
      "age": 20,
      "course": "Computer Science",
      "email": "ada@example.com"
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 10,
  "pages": 1
}
```

### Example protected request

Create a student:

```bash
curl -X POST http://127.0.0.1:8000/students \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"name":"Ada Lovelace","age":20,"course":"Computer Science","email":"ada@example.com"}'
```

List students:

```bash
curl "http://127.0.0.1:8000/students?page=1&page_size=10" \
  -H "Authorization: Bearer <access_token>"
```

Update a student:

```bash
curl -X PUT http://127.0.0.1:8000/students/1 \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"name":"Ada Byron","age":21,"course":"Mathematics","email":"ada.byron@example.com"}'
```

Delete a student:

```bash
curl -X DELETE http://127.0.0.1:8000/students/1 \
  -H "Authorization: Bearer <access_token>"
```

---

## Error Handling

| Status | When |
| --- | --- |
| `401 Unauthorized` | Missing, invalid, tampered, or expired token; wrong login credentials |
| `404 Not Found` | Student ID does not exist |
| `409 Conflict` | Duplicate user email or duplicate student email |
| `422 Unprocessable Entity` | Invalid input or invalid pagination parameters |
| `500 Internal Server Error` | Database failure; the session is rolled back and internals are not exposed |

Authentication failures return a generic message, so it is not possible to
distinguish an unknown email from a wrong password.

### Request and error lifecycle graph

```mermaid
flowchart TD
    Request["Incoming request"] --> Validate["Pydantic validation"]
    Validate -->|"invalid"| E422["422 Unprocessable Entity"]
    Validate -->|"valid"| AuthCheck{"Valid Bearer JWT?"}
    AuthCheck -->|"no"| E401["401 Unauthorized"]
    AuthCheck -->|"yes"| Handler["Route handler"]
    Handler --> DB[("PostgreSQL")]
    DB -->|"duplicate email"| E409["Rollback + 409 Conflict"]
    DB -->|"other database error"| E500["Rollback + 500 Internal Server Error"]
    DB -->|"success"| Response["Typed response model"]
    Response --> Client["Client receives JSON"]
```

---

## Security

- Passwords are hashed with **Argon2**; plaintext passwords are never stored.
- API responses never include `hashed_password`.
- JWTs are signed with `JWT_SECRET_KEY` and include `sub`, `iat`, and `exp`
  claims.
- Expired and tampered tokens are rejected.
- Login errors are deliberately generic.
- Database sessions are closed in `finally` and rolled back on exceptions.
- `.env` is git-ignored; only `.env.example` placeholders are committed.
- Configuration is validated at startup; weak or placeholder secrets are
  rejected.
- JWT algorithms are restricted to `HS256`, `HS384`, and `HS512`.

---

## Testing

The automated suite uses FastAPI `TestClient` with an isolated in-memory SQLite
database. It never touches PostgreSQL data.

Run all tests:

```bash
python -m pytest -v
```

Run a single test file:

```bash
python -m pytest tests/test_auth.py -v
```

### Test matrix

| Area | Coverage |
| --- | --- |
| Authentication | Signup, duplicate signup, login, wrong password, unknown email, `/auth/me` |
| Security / JWT | Hashing, verification, token generation, decoding, expiration, tampering |
| Students | Create, list, get, update, delete, duplicate email, missing IDs |
| Pagination | Page/page-size behavior and invalid parameters |
| Validation | Invalid email, short password, blank fields, invalid age |
| Authorization | Missing, invalid, expired, and unknown-user tokens |
| Configuration | Short/placeholder secrets and unsafe algorithms |

### Test coverage graph

```mermaid
pie title Automated tests by area
    "Authentication" : 11
    "Security and JWT" : 6
    "Students" : 15
    "Configuration" : 4
```

**Verified result on Python 3.12.10:** `36 passed, 0 failed`.

Manual diagnostics:

```bash
python scripts/check_db.py
python scripts/check_security.py
```

---

## Troubleshooting

| Symptom | Resolution |
| --- | --- |
| `ModuleNotFoundError` | Activate the virtual environment and run `pip install -r requirements.txt` |
| `JWT_SECRET_KEY is still a placeholder` | Replace it with a generated secret in `.env` |
| `JWT_SECRET_KEY` validation error | Use at least 32 characters |
| Database connection failed | Check `DATABASE_URL`, confirm PostgreSQL is running, and verify credentials |
| `psql` is not recognized | Add PostgreSQL's `bin` directory to `PATH` or use the full path |
| `401` after login | Include the `Bearer ` prefix and confirm the token has not expired |
| `409` on student create | Use a unique student email |
| `422` on student create | Check field lengths, age range, course, and email format |

---

## Production Hardening

This repository is portfolio-grade and intentionally focused on API design,
authentication, validation, and testing. For a production deployment, consider:

- **Alembic** for versioned, repeatable schema migrations.
- **HTTPS** termination and secure headers at a reverse proxy.
- **Rate limiting** on `/auth/login` and signup endpoints.
- **Refresh tokens and token revocation** if long-lived sessions are required.
- **CORS configuration** for known frontend origins.
- **Secrets management** through a vault or cloud secret store.
- **Observability** with structured logs, metrics, and tracing.
- **Managed PostgreSQL** with backups, connection pooling, and monitoring.
- **CI/CD** running `pytest` on every pull request.

---

## Author

Maintained by [@pshkarsngh](https://github.com/pshkarsngh).

Repository: [Student_Management_System](https://github.com/pshkarsngh/Student_Management_System)
