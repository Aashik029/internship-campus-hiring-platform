import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base, get_db
from app.main import app

# CI sets DATABASE_URL to a Postgres 15 service so the suite runs against the
# same engine family as production. Local runs default to in-memory SQLite.
_DATABASE_URL = os.environ.get("DATABASE_URL", "")
if _DATABASE_URL:
    engine = create_engine(_DATABASE_URL)
else:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


@pytest.fixture()
def client():
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)


def register_student(
    client, email="student@test.com", password="secret123", name="Test Student"
):
    return client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": password,
            "full_name": name,
            "role": "student",
        },
    )


def register_company(
    client, email="company@test.com", password="secret123", name="Test Corp"
):
    return client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": password,
            "full_name": name,
            "role": "company",
        },
    )


def auth_header(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}
