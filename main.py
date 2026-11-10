
from fastapi import FastAPI
from pydantic import BaseModel


# Student data model
class Student(BaseModel):
    name: str
    age: int
    course: str


# Create FastAPI application
app = FastAPI(
    title="Student Management API",
    description="Backend for managing students",
    version="1.0.0"
)


# Temporary storage
students = []


# Home route
@app.get("/")
def home():
    return {
        "message": "Student Management Backend is running"
    }


# Add a new student
@app.post("/students")
def add_student(student: Student):

    student_data = {
        "id": len(students) + 1,
        "name": student.name,
        "age": student.age,
        "course": student.course
    }

    students.append(student_data)

    return {
        "message": "Student added successfully",
        "student": student_data
    }


# Get all students
@app.get("/students")
def get_students():
    return {
        "students": students
    }
    # Update student details
@app.put("/students/{student_id}")
def update_student(student_id: int, updated_student: Student):

    for student in students:
        if student["id"] == student_id:

            student["name"] = updated_student.name
            student["age"] = updated_student.age
            student["course"] = updated_student.course

            return {
                "message": "Student updated successfully",
                "student": student
            }

    return {
        "message": "Student not found"
    }


# Get a student by ID
@app.get("/students/{student_id}")
def get_student(student_id: int):

    for student in students:
        if student["id"] == student_id:
            return {
                "student": student
            }

    return {
        "message": "Student not found"
    }
