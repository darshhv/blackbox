"""
BLACKBOX Database Configuration
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base
import os

# Database URL - defaults to local PostgreSQL
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://blackbox:blackbox@localhost:5432/blackbox"
)

# Create engine
engine = create_engine(DATABASE_URL, echo=True)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """
    Initialize database tables.
    Called on application startup.
    """
    Base.metadata.create_all(bind=engine)
    print("Database initialized successfully")


def get_db():
    """
    Dependency for FastAPI endpoints.
    Yields a database session and ensures cleanup.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
