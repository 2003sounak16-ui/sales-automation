import os
import json
import pytest
from unittest.mock import MagicMock, patch
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

@pytest.fixture
def mock_groq_completion(monkeypatch):
    """
    Mocks Groq client LLM completion to return deterministic JSON without API calls.
    """
    mock_choice = MagicMock()
    mock_choice.message.content = json.dumps({
        "subject": "Accelerate Sales with AI Automation",
        "body": "Hi there,\n\nWe noticed your innovation in the industry and would love to collaborate.\n\nBest,\nSalesFlow AI"
    })
    mock_completion = MagicMock()
    mock_completion.choices = [mock_choice]

    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = mock_completion

    monkeypatch.setattr("services.ai.groq_client.get_groq_client", lambda: mock_client)
    return mock_client

@pytest.fixture
def mock_smtp_send(monkeypatch):
    """
    Mocks outreach email dispatch via SMTP to avoid external network calls.
    """
    mock_result = {
        "status": "success",
        "id": "mock-smtp-9999",
        "message": "Email successfully dispatched to recipient@example.com"
    }
    mock_send = MagicMock(return_value=mock_result)
    monkeypatch.setattr("services.email.smtp_client.send_outreach_email_via_smtp", mock_send)
    monkeypatch.setattr("api.email.send_outreach_email_via_smtp", mock_send)
    return mock_send

@pytest.fixture
def mock_ddg_search(monkeypatch):
    """
    Mocks DuckDuckGo company search and discovery.
    """
    mock_results = [
        {"company": "Acme Robotics", "website": "https://acme-robotics.com"},
        {"company": "Beta Cloud", "website": "https://betacloud.io"}
    ]
    mock_discover = MagicMock(return_value=mock_results)
    monkeypatch.setattr("services.discovery.duckduckgo.DuckDuckGoDiscovery.discover_companies", mock_discover)
    return mock_discover
