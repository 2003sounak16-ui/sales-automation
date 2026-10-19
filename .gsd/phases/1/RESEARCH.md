# Phase 1 Research: Test Infrastructure & Mock Services

> Researched on 2026-10-19 for Phase 1

## Objective
Establish a zero-cost, deterministic, and fast backend testing foundation for FastAPI using `pytest`, isolated database fixtures, and mocks for external AI/Email/Search services.

## Findings

### 1. Test Harness Dependencies
- **`pytest`**: Core test runner.
- **`pytest-asyncio`**: Required for testing async FastAPI endpoints and asynchronous database utilities.
- **`httpx`**: Used by FastAPI's `TestClient` to dispatch in-memory HTTP requests without starting a network server socket.

### 2. Database Isolation Strategy
- `backend/database/connection.py` provides `SQLiteFallbackClient(db_path=...)`.
- Using a test fixture with `tmp_path / "test.db"` or in-memory SQLite ensures:
  1. Complete isolation between test runs.
  2. No pollution of `backend/local_db.sqlite`.
  3. Automatic schema initialization (`leads` and `lead_events` tables).

### 3. Mock Fixtures for Third-Party APIs
- **Groq LLM**:
  - `services/ai/groq_client.py` instantiates `Groq(api_key=...)`.
  - Mock fixture replaces `client.chat.completions.create` with a mock response returning valid JSON (e.g., subject line and pitch body).
- **Resend Email API**:
  - `api/email.py` calls `resend.Emails.send(...)`.
  - Mock fixture intercepts `resend.Emails.send` and returns `{"id": "mock-email-uuid"}`.
- **DuckDuckGo Search**:
  - `services/discovery/duckduckgo.py` calls `duckduckgo_search.DDGS().text(...)`.
  - Mock fixture returns simulated domain search results to test the discovery and scraping pipeline deterministically.

### 4. Project Layout
- Place tests under `backend/tests/`:
  - `backend/tests/conftest.py`: Shared fixtures (test client, isolated db, mocked services).
  - `backend/tests/test_health.py`: Baseline smoke test for FastAPI and health check probe.
- `backend/pytest.ini`: Configures test discovery, python path, and asyncio defaults.
