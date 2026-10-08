"""Fixtures communes : client FastAPI et JWT obtenus par un vrai login."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.config import TEST_DATABASE_URL
from backend.init_db import init_db
from backend.main import app


engine_test = create_engine(TEST_DATABASE_URL, pool_pre_ping=True)
sessionTest = sessionmaker(bind=engine_test, autoflush=False, autocommit=False)

ANALYST = {"username": "analyst01", "password": "Analyst2026!"}
READER = {"username": "reader01", "password": "Reader2026!"}


@pytest.fixture(scope="session")
def client():
    """Client HTTP en mémoire branché sur la vraie base PostgreSQL."""

    # Garantit la présence des comptes et des 24 observations.
    init_db()
    with TestClient(app) as test_client:
        yield test_client


def _login(client: TestClient, credentials: dict) -> str:
    response = client.post("/auth/login", json=credentials)
    assert response.status_code == 200, response.text
    return response.json()["access_token"]


@pytest.fixture(scope="session")
def analyst_token(client):
    """JWT récupéré via POST /auth/login avec le compte analyst."""
    return _login(client, ANALYST)


@pytest.fixture(scope="session")
def reader_token(client):
    """JWT récupéré via POST /auth/login avec le compte reader."""
    return _login(client, READER)
