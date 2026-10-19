---
phase: 1
plan: 1
wave: 1
depends_on: []
gap_closure: false
---

# Plan 1.1: Pytest Configuration and Test Database Harness

## Objective
Configure the pytest testing framework for the FastAPI backend and implement an isolated test database harness that ensures tests run with clean, disposable SQLite state without polluting the local database.

## Context
Load these files for context:
- `.gsd/SPEC.md`
- `.gsd/ARCHITECTURE.md`
- `backend/requirements.txt`
- `backend/database/connection.py`
- `backend/main.py`

## Tasks

<task type="auto">
  <name>Configure pytest and testing dependencies</name>
  <files>
    backend/requirements.txt
    backend/pytest.ini
  </files>
  <action>
    1. Update `backend/requirements.txt` to include test dependencies: `pytest>=8.0.0` and `pytest-asyncio>=0.23.0`.
    2. Create `backend/pytest.ini` with:
       - `testpaths = tests`
       - `pythonpath = .`
       - `asyncio_mode = auto`
       - `-v` verbosity flag
    AVOID: hardcoding external absolute paths.
    USE: relative paths rooted in `backend/`.
  </action>
  <verify>
    Check that pytest.ini exists and has testpaths and pythonpath configured.
  </verify>
  <done>
    Requirements file contains pytest packages and pytest.ini is created.
  </done>
</task>

<task type="auto">
  <name>Create test directory and isolated database test harness</name>
  <files>
    backend/tests/__init__.py
    backend/tests/conftest.py
  </files>
  <action>
    1. Create `backend/tests/__init__.py`.
    2. Create `backend/tests/conftest.py` defining:
       - An `isolated_db` pytest fixture using `SQLiteFallbackClient` pointed to a temporary file (`tmp_path / "test_local.sqlite"`).
       - Monkeypatch `database.connection.db_client` and `database.connection.get_db` to return the test client during tests.
       - A `test_client` fixture using FastAPI's `TestClient(app)` from `fastapi.testclient`.
    AVOID: Using the production `local_db.sqlite` during tests.
    USE: `tmp_path` fixture for per-test isolation.
  </action>
  <verify>
    Verify conftest.py defines `isolated_db` and `test_client` fixtures.
  </verify>
  <done>
    Pytest fixtures load clean test database without touching local_db.sqlite.
  </done>
</task>
