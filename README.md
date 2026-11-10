# Student Management System API

A secure, production-style **Student Management System** backend built with
**FastAPI**, **PostgreSQL**, **SQLAlchemy**, **Pydantic**, **Argon2** password
hashing, and **JWT** authentication.

Authenticated users can create, list, view, update, and delete student records.
Student routes are protected with bearer tokens, passwords are never stored or
returned in plaintext, and all secrets are loaded from environment variables.

---

## Features

- User signup and login with Argon2 password hashing.
- JWT access tokens with configurable expiration.
- `GET /auth/me` current-user endpoint.
- Bearer-token protection on every student endpoint.
- Full student CRUD with duplicate-email protection.
- Pagination on `GET /students`.
- Strict Pydantic request validation and typed response schemas.
- Safe database error handling with rollback.
- Modern FastAPI lifespan startup (no deprecated `on_event`).
- Automated pytest suite using FastAPI `TestClient` and an isolated SQLite
  database.
- Secrets kept in `.env`; `.env` is git-ignored.

---

## Technologies

| Layer | Technology |
| --- | --- |
| Language | Python 3.12 |
| Web framework | FastAPI |
| Database | PostgreSQL |
| ORM | SQLAlchemy 2.x |
| Validation | Pydantic 2.x / pydantic-settings |
| Password hashing | Argon2 via `pwdlib[argon2]` |
| Authentication | JWT via PyJWT |
| Testing | pytest + FastAPI TestClient |

---

## Project Structure

```text
Student_management_System/
├── main.py                 # FastAPI app, lifespan, router registration
├── config.py               # Typed environment settings
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
│   ├── test_security.py
│   └── test_students.py
├── .env.example            # Placeholder configuration (safe to commit)
├── pytest.ini
├── requirements.txt
└── README.md
```

---

## Installation

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

## Environment Configuration

Copy the example file and fill in your own values:

Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

macOS / Linux:

```bash
cp .env.example .env
```

`.env`:

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

Rules:

- Never commit `.env`.
- Never hardcode database passwords or JWT secrets in source code.
- `JWT_SECRET_KEY` must be at least 32 characters.
- The application refuses to start if `JWT_SECRET_KEY` is still the example
  placeholder.
- `ACCESS_TOKEN_EXPIRE_MINUTES` controls token lifetime (default `30`).

---

## Database Setup

### Create the PostgreSQL database

Using `psql`:

```sql
CREATE DATABASE student_management;
```

Or using `createdb`:

```bash
createdb student_management
```

### Tables

Tables are created automatically on application startup through the FastAPI
lifespan handler:

- `students`
- `users`

### Existing database migration

The current application requires `students.course` to be `NOT NULL`. Fresh
databases get this automatically. If you are upgrading an older database where
`course` is nullable, apply the safe migration:

```bash
psql "$DATABASE_URL" -f migrations/001_students_course_not_null.sql
```

Windows PowerShell:

```powershell
psql $env:DATABASE_URL -f migrations/001_students_course_not_null.sql
```

The migration does **not** delete or recreate the database or any rows. If a
row contains a `NULL` course, the `SET NOT NULL` statement fails safely and the
transaction rolls back; fix that row and run it again.

### Verify the connection

```bash
python scripts/check_db.py
```

Expected output:

```text
PostgreSQL connected successfully!
```

---

## Running the Application

From the project root with the virtual environment active:

```bash
uvicorn main:app --reload
```

Or with the FastAPI CLI:

```bash
fastapi dev main.py
```

The API is available at:

- API root: <http://127.0.0.1:8000/>
- Swagger UI: <http://127.0.0.1:8000/docs>
- ReDoc: <http://127.0.0.1:8000/redoc>
- OpenAPI JSON: <http://127.0.0.1:8000/openapi.json>

---

## Authentication

Authentication uses OAuth2 password flow with bearer JWTs.

1. Create an account with `POST /auth/signup`.
2. Log in with `POST /auth/login` using form data.
3. Send the returned token as `Authorization: Bearer <access_token>`.
4. Access protected routes such as `/students` and `/auth/me`.

In Swagger UI, click **Authorize**, enter your email as the username and your
password, and Swagger will attach the token automatically.

### Signup

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

### Login

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

### Current user

```bash
curl http://127.0.0.1:8000/auth/me \
  -H "Authorization: Bearer <access_token>"
```

---

## API Endpoints

### Public

| Method | Endpoint | Description | Success |
| --- | --- | --- | --- |
| `GET` | `/` | Health/landing endpoint | `200` |
| `POST` | `/auth/signup` | Register a user | `201` |
| `POST` | `/auth/login` | Obtain a JWT (form data) | `200` |

### Protected — require `Authorization: Bearer <token>`

| Method | Endpoint | Description | Success |
| --- | --- | --- | --- |
| `GET` | `/auth/me` | Current authenticated user | `200` |
| `POST` | `/students` | Create a student | `201` |
| `GET` | `/students?page=1&page_size=10` | Paginated student list | `200` |
| `GET` | `/students/{student_id}` | Get one student | `200` |
| `PUT` | `/students/{student_id}` | Replace student details | `200` |
| `DELETE` | `/students/{student_id}` | Delete a student | `200` |

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

### Student request body

```json
{
  "name": "Ada Lovelace",
  "age": 20,
  "course": "Computer Science",
  "email": "ada@example.com"
}
```

Validation rules:

- `name`: 2–100 characters, not blank.
- `age`: integer greater than `0` and at most `120`.
- `course`: 2–100 characters, not blank.
- `email`: valid email address; stored lowercase.
- `password` (signup): 8–128 characters.

### Example protected request

```bash
curl -X POST http://127.0.0.1:8000/students \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"name":"Ada Lovelace","age":20,"course":"Computer Science","email":"ada@example.com"}'
```

---

## Error Handling

| Status | When |
| --- | --- |
| `401 Unauthorized` | Missing, invalid, tampered, or expired token; wrong login credentials |
| `404 Not Found` | Student ID does not exist |
| `409 Conflict` | Duplicate user email or duplicate student email |
| `422 Unprocessable Entity` | Invalid input or invalid pagination parameters |
| `500 Internal Server Error` | Database failure; the session is rolled back and no internals are exposed |

Authentication failures return a generic message so it is not possible to
distinguish an unknown email from a wrong password.

---

## Security Notes

- Passwords are hashed with Argon2; plaintext passwords are never stored.
- API responses never include `hashed_password`.
- JWT tokens are signed with `JWT_SECRET_KEY` and include `sub`, `iat`, and
  `exp` claims.
- Expired and tampered tokens are rejected.
- Login errors are deliberately generic.
- Database sessions are closed in `finally`, and rolled back on exceptions.
- `.env` is git-ignored; only `.env.example` placeholders are committed.
- Configuration is validated at startup; the app will not start with a missing
  or too-short JWT secret.

---

## Testing

The automated suite uses FastAPI `TestClient` with an isolated in-memory SQLite
database. It never touches your PostgreSQL data.

Run all tests:

```bash
python -m pytest -v
```

Run a single file:

```bash
python -m pytest tests/test_auth.py -v
```

Coverage includes:

- Signup success, duplicate signup, invalid email, short password.
- Login success, wrong password, unknown email.
- JWT generation, decoding, expiration, tampering.
- Missing/invalid token rejection on protected routes.
- `/auth/me` success and failure cases.
- Authenticated student create, list, get, update, delete.
- Duplicate student email handling.
- Pagination and invalid pagination parameters.
- Invalid student input and missing student IDs.
- Expired token and token-for-unknown-user rejection.
- Configuration validation (short/placeholder secrets and unsafe algorithms).

**Verified result on Python 3.12.10:**

```text
36 passed in 2.16s
```

Manual diagnostics:

```bash
python scripts/check_db.py
python scripts/check_security.py
```

---

## Git / GitHub Readiness

`.gitignore` excludes:

- `venv/` and `.venv/`
- `__pycache__/` and Python bytecode
- `.env` and other local env files
- test/cache artifacts
- local SQLite databases

Only `.env.example` is committed. Before pushing, confirm:

```bash
git status
git check-ignore -v .env
```

`.env` should be ignored and must never appear in Git history.
