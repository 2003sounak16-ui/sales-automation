# SPEC.md — Project Specification

> **Status**: `FINALIZED`
>
> ⚠️ **Planning Lock**: No code may be written until this spec is marked `FINALIZED`.

## Vision
Harden the SalesFlow Automation Hub with an automated testing infrastructure, mocked third-party service fixtures, and resilient scraper error handling to ensure rock-solid stability and zero-cost, deterministic local and CI test execution.

## Goals
1. **Automated Backend Test Infrastructure**: Set up `pytest` framework, configuration, and reusable fixtures for database connections and HTTP clients.
2. **Deterministic Third-Party Mocking**: Provide mock fixtures for Groq LLM inference, Resend email dispatch, and DuckDuckGo web discovery so tests run offline, rapidly, and without incurring API costs.
3. **Comprehensive API Route Coverage**: Implement unit and integration tests covering all FastAPI endpoints (`/api/company`, `/api/review`, `/api/email`, `/api/dashboard`, `/api/health`).
4. **Data Layer Testing**: Validate SQLite fallback operations, JSON serialization, and lead/event CRUD integrity under edge cases.
5. **Scraper Resilience & Error Recovery**: Harden web scraping and contact extraction against network timeouts, SSL anomalies, anti-bot challenges, and missing email contacts.

## Non-Goals (Out of Scope)
- Developing new frontend feature views or altering the core SDR workflow during this milestone.
- Executing live, paid third-party API calls during routine CI or test suite runs.
- Introducing heavy browser-automation headless drivers (e.g. Selenium/Playwright) for basic web scraping.

## Users
- **Backend Engineers & Developers**: Run fast, deterministic unit and integration tests locally.
- **SDRs & Sales Teams**: Benefit from an uncrashable lead extraction and outreach generation pipeline.

## Constraints
- **Runtime**: Python 3.11+ compatibility.
- **Cross-Platform**: Tests must execute reliably on both Windows and Linux environments.
- **Execution Speed**: The complete unit test suite should execute in under 10 seconds.

## Success Criteria
- [ ] Pytest test suite configured and passing 100% of test cases.
- [ ] All primary FastAPI routes covered by automated tests.
- [ ] Mock fixtures in place for Groq, Resend, and DuckDuckGo.
- [ ] Scraper gracefully handles invalid URLs, timeouts, and missing contacts without unhandled exceptions.
