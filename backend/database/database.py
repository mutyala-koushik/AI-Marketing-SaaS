from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


# Project database path
BASE_DIR = Path(__file__).resolve().parent
DATABASE_URL = f"sqlite:///{BASE_DIR / 'app.db'}"


# SQLite engine
engine = create_engine(
    DATABASE_URL,
    connect_args={
        "check_same_thread": False
    },
)


# Database session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


# Base class for SQLAlchemy models
Base = declarative_base()


def get_db():
    """
    Provide a database session to FastAPI routes.
    """
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()