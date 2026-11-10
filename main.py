"""FastAPI application entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from database import create_tables
from routers import auth, students


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create any missing tables when the application starts."""

    create_tables()
    yield


app = FastAPI(
    title="Student Management API",
    description=(
        "A secure Student Management System backend with JWT authentication. "
        "Sign up or log in via /auth, then use the bearer token to manage "
        "students."
    ),
    version="2.0.0",
    lifespan=lifespan,
)

app.include_router(auth.router)
app.include_router(students.router)


@app.get("/", tags=["Health"])
def home() -> dict[str, str]:
    """Public health/landing endpoint."""

    return {"message": "Student Management Backend is running"}
