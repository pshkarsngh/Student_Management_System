"""SQLAlchemy database models."""

from sqlalchemy import Column, Integer, String

from database import Base


class Student(Base):
    """A student record managed by authenticated users."""

    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    age = Column(Integer, nullable=False)
    course = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)


class User(Base):
    """An application user who can sign in and manage students."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
