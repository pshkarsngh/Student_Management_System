"""Student management routes (authentication required)."""

import logging
import math

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from database import get_db
from dependencies import get_current_user
from models import Student
from schemas import (
    StudentCreate,
    StudentDeleteResponse,
    StudentListResponse,
    StudentMessageResponse,
    StudentResponse,
    StudentUpdate,
)

logger = logging.getLogger(__name__)

# Every route in this router requires a valid JWT.
router = APIRouter(
    prefix="/students",
    tags=["Students"],
    dependencies=[Depends(get_current_user)],
)


def _get_student_or_404(db: Session, student_id: int) -> Student:
    student = db.get(Student, student_id)
    if student is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found",
        )
    return student


@router.post(
    "",
    response_model=StudentMessageResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add a new student",
)
def add_student(
    student_in: StudentCreate,
    db: Session = Depends(get_db),
) -> StudentMessageResponse:
    """Create a student after checking for a duplicate email."""

    existing_student = (
        db.query(Student).filter(Student.email == student_in.email).first()
    )
    if existing_student is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Student with this email already exists",
        )

    student = Student(**student_in.model_dump())
    db.add(student)

    try:
        db.commit()
        db.refresh(student)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Student with this email already exists",
        ) from None
    except SQLAlchemyError:
        db.rollback()
        logger.exception("Database error while creating a student")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="A database error occurred",
        ) from None

    return StudentMessageResponse(
        message="Student added successfully",
        student=StudentResponse.model_validate(student),
    )


@router.get(
    "",
    response_model=StudentListResponse,
    summary="List students with pagination",
)
def get_students(
    page: int = Query(default=1, ge=1, description="Page number (1-based)"),
    page_size: int = Query(
        default=10,
        ge=1,
        le=100,
        description="Number of students per page",
    ),
    db: Session = Depends(get_db),
) -> StudentListResponse:
    """Return a paginated, stable (ID-ordered) list of students."""

    total = db.query(Student).count()
    students = (
        db.query(Student)
        .order_by(Student.id)
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return StudentListResponse(
        students=[StudentResponse.model_validate(s) for s in students],
        total=total,
        page=page,
        page_size=page_size,
        pages=math.ceil(total / page_size) if total else 0,
    )


@router.get(
    "/{student_id}",
    response_model=StudentResponse,
    summary="Get a student by ID",
)
def get_student(
    student_id: int,
    db: Session = Depends(get_db),
) -> Student:
    """Return a single student or 404 when it does not exist."""

    return _get_student_or_404(db, student_id)


@router.put(
    "/{student_id}",
    response_model=StudentMessageResponse,
    summary="Update a student",
)
def update_student(
    student_id: int,
    student_in: StudentUpdate,
    db: Session = Depends(get_db),
) -> StudentMessageResponse:
    """Replace a student's details, guarding against duplicate emails."""

    student = _get_student_or_404(db, student_id)

    existing_email = (
        db.query(Student)
        .filter(
            Student.email == student_in.email,
            Student.id != student_id,
        )
        .first()
    )
    if existing_email is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already belongs to another student",
        )

    for field, value in student_in.model_dump().items():
        setattr(student, field, value)

    try:
        db.commit()
        db.refresh(student)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already belongs to another student",
        ) from None
    except SQLAlchemyError:
        db.rollback()
        logger.exception("Database error while updating a student")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="A database error occurred",
        ) from None

    return StudentMessageResponse(
        message="Student updated successfully",
        student=StudentResponse.model_validate(student),
    )


@router.delete(
    "/{student_id}",
    response_model=StudentDeleteResponse,
    summary="Delete a student",
)
def delete_student(
    student_id: int,
    db: Session = Depends(get_db),
) -> StudentDeleteResponse:
    """Delete a student and return the removed record."""

    student = _get_student_or_404(db, student_id)
    deleted_student = StudentResponse.model_validate(student)

    try:
        db.delete(student)
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        logger.exception("Database error while deleting a student")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="A database error occurred",
        ) from None

    return StudentDeleteResponse(
        message="Student deleted successfully",
        student=deleted_student,
    )
