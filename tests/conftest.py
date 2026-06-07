from datetime import date

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models import Task

TEST_DATABASE_URL = "sqlite://"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session() -> Session:
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def sample_task(client):
    response = client.post(
        "/tasks",
        json={
            "title": "Sample task",
            "status": "pending",
            "priority": "medium",
        },
    )
    assert response.status_code == 201
    return response.json()


def add_task(
    db: Session,
    *,
    title: str,
    status: str = "pending",
    priority: str = "medium",
    created_at: date,
) -> Task:
    task = Task(
        title=title,
        status=status,
        priority=priority,
        created_at=created_at,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task
