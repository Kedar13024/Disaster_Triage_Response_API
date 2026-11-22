# tests/conftest.py

import pytest
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from sqlalchemy import URL, create_engine

from main import app
from backend.core.config import get_settings
from backend.database.database import Base , get_db
from backend.models import models

settings = get_settings()

TEST_DATABASE_URL = URL.create(
    drivername="postgresql+psycopg2",
    username=settings.database_user,
    password=settings.database_password,
    host=settings.database_host,
    port=settings.database_port,
    database="dtr_db_test",
)

test_engine = create_engine(TEST_DATABASE_URL)


TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine,
)


@pytest.fixture
def db_session():
    Base.metadata.create_all(bind=test_engine)

    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def client(db_session):

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.pop(get_db, None)


@pytest.fixture
def user_payload():
    return {
        "user_fullname": "Test Citizen",
        "user_phoneno": "+919876543210",
        "user_email": "citizen_test@example.com",
        "user_password": "TestPassword123!",
    }