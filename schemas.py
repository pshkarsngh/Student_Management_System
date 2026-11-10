"""Pydantic request and response schemas."""

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class UserCreate(BaseModel):
    """Payload for user signup."""

    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return value.strip().lower()


class UserResponse(BaseModel):
    """Public representation of a user. Never includes password material."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr


class Token(BaseModel):
    """OAuth2-style access token response."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int = Field(..., description="Token lifetime in seconds")


class StudentBase(BaseModel):
    """Fields shared by student create and update requests."""

    name: str = Field(..., min_length=2, max_length=100)
    age: int = Field(..., gt=0, le=120)
    course: str = Field(..., min_length=2, max_length=100)
    email: EmailStr

    @field_validator("name", "course")
    @classmethod
    def strip_and_reject_blank(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("must not be blank")
        return cleaned

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return value.strip().lower()


class StudentCreate(StudentBase):
    """Payload for creating a student."""


class StudentUpdate(StudentBase):
    """Payload for replacing a student's details."""


class StudentResponse(StudentBase):
    """Public representation of a student."""

    model_config = ConfigDict(from_attributes=True)

    id: int


class StudentListResponse(BaseModel):
    """Paginated student list."""

    students: list[StudentResponse]
    total: int
    page: int
    page_size: int
    pages: int


class StudentMessageResponse(BaseModel):
    """Confirmation payload returned after create/update."""

    message: str
    student: StudentResponse


class StudentDeleteResponse(BaseModel):
    """Confirmation payload returned after delete."""

    message: str
    student: StudentResponse
