
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
