from fastapi import status

def test_root_endpoint(test_client):
    """
    Verify root endpoint returns HTTP 200 and expected welcome message.
    """
    response = test_client.get("/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "message" in data
    assert data["message"] == "Welcome to the Sales Automation API"

def test_health_check_endpoint(test_client):
    """
    Verify /api/health endpoint returns HTTP 200 and healthy status.
    """
    response = test_client.get("/api/health")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data.get("status") == "healthy"

def test_mock_groq_fixture(mock_groq_completion):
    """
    Verify mock Groq LLM fixture intercepts client instantiation.
    """
    from services.ai.groq_client import get_groq_client
    client = get_groq_client()
    assert client is not None
    completion = client.chat.completions.create()
    assert len(completion.choices) == 1
    assert "Accelerate Sales" in completion.choices[0].message.content

def test_mock_smtp_fixture(mock_smtp_send):
    """
    Verify mock SMTP email fixture intercepts outbound email sending.
    """
    from services.email.smtp_client import send_outreach_email_via_smtp
    res = send_outreach_email_via_smtp("test@example.com", "Subject", "Body")
    assert res["status"] == "success"
    assert res["id"] == "mock-smtp-9999"

def test_mock_ddg_fixture(mock_ddg_search):
    """
    Verify mock DuckDuckGo search fixture intercepts company discovery.
    """
    from services.discovery.duckduckgo import DuckDuckGoDiscovery
    discovery = DuckDuckGoDiscovery()
    results = discovery.discover_companies("Technology")
    assert len(results) == 2
    assert results[0]["company"] == "Acme Robotics"

