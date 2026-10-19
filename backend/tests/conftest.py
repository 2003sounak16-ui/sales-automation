import os
import pytest
from fastapi.testclient import TestClient
from database.connection import SQLiteFallbackClient
import database.connection as db_conn
from main import app

@pytest.fixture(autouse=True)
def isolated_db(tmp_path, monkeypatch):
    """
    Creates an isolated SQLite test database for each test run.
    Ensures zero interaction with local_db.sqlite or external Supabase instance.
    """
    test_db_path = str(tmp_path / "test_pipeline.sqlite")
    client = SQLiteFallbackClient(db_path=test_db_path)
    monkeypatch.setattr(db_conn, "db_client", client)
    monkeypatch.setattr(db_conn, "get_db", lambda: client)
    yield client
    if hasattr(client, "conn") and client.conn:
        client.conn.close()

@pytest.fixture
def test_client(isolated_db):
    """
    Provides a FastAPI TestClient configured with the isolated database.
    """
    return TestClient(app)
