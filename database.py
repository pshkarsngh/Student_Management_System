
import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Load environment variables from .env file
load_dotenv()

# Read database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")

# Check whether database URL exists
if not DATABASE_URL:
    raise ValueError("DATABASE_URL is missing. Check your .env file.")

# Create PostgreSQL engine
engine = create_engine(DATABASE_URL)

# Create database session
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base class for database models
Base = declarative_base()


# Database dependency for FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
