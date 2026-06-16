import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://postgres:postgres@db:5432/messages")

engine = create_engine(DATABASE_URL)
TestSession = sessionmaker(bind=engine)


@pytest.fixture(autouse=True)
def clean_db():
    """Clear messages table before each test."""
    with engine.connect() as conn:
        conn.execute(text("DELETE FROM messages"))
        conn.commit()
    yield


@pytest.fixture
def client():
    def override_get_db():
        db = TestSession()
        try:
            yield db
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
