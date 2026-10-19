---
phase: 1
plan: 2
wave: 2
depends_on:
  - 1-PLAN.md
gap_closure: false
---

# Plan 1.2: Deterministic Mock Fixtures and Baseline Health Tests

## Objective
Implement reusable mock fixtures for external AI (Groq), Email (Resend), and Search (DuckDuckGo) services, and verify the test harness with baseline tests for `/api/health` and root routes.

## Context
Load these files for context:
- `.gsd/SPEC.md`
- `.gsd/phases/1/1-PLAN.md`
- `backend/tests/conftest.py`
- `backend/api/health.py`
- `backend/services/ai/groq_client.py`

## Tasks

<task type="auto">
  <name>Implement mock fixtures for external services</name>
  <files>
    backend/tests/conftest.py
  </files>
  <action>
    1. In `backend/tests/conftest.py`, add mock fixtures:
       - `mock_groq_completion`: Mocks Groq client completions with synthetic subject and email body JSON.
       - `mock_resend_send`: Mocks `resend.Emails.send` returning `{"id": "mock-email-id-12345"}`.
       - `mock_ddg_search`: Mocks `duckduckgo_search.DDGS.text` returning sample search snippets.
    AVOID: Making real network calls to Groq or Resend in tests.
    USE: `unittest.mock.patch` to guarantee deterministic offline execution.
  </action>
  <verify>
    Verify mock fixtures can be imported and utilized in test functions.
  </verify>
  <done>
    Fixtures intercept network requests and return mock payloads.
  </done>
</task>

<task type="auto">
  <name>Create baseline health check and root endpoint tests</name>
  <files>
    backend/tests/test_health.py
  </files>
  <action>
    1. Create `backend/tests/test_health.py` with tests for:
       - Root endpoint `GET /` returns status 200 and welcome message.
       - Health check `GET /api/health` returns status 200 and healthy status.
    2. Run pytest to verify the full harness executes cleanly.
    USE: `test_client` fixture created in Plan 1.1.
  </action>
  <verify>
    Run: `pytest` inside `backend/` and assert all tests pass.
  </verify>
  <done>
    `pytest` runs, discovers `test_health.py`, and passes with 100% success.
  </done>
</task>
