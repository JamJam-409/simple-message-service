import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
print(engine.url)


class Base(DeclarativeBase):
    """Base class for SQLAlchemy declarative models."""

    pass


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Provide a database session for a single request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
