# Decisions — Architecture Decision Records

> **Purpose**: Log significant technical decisions and their rationale.

## Decisions

### [DECISION-001] Automated Testing Strategy with Pytest and Mock Fixtures

**Date**: 2026-10-19
**Status**: Accepted

#### Context
The SalesFlow Automation Hub currently lacks automated unit and integration tests. Outbound email dispatch (Resend) and LLM copy generation (Groq) incur rate limits and monetary costs, while external web scraping introduces non-deterministic network latency.

#### Decision
Adopt `pytest` as the test framework, with modular mock fixtures for Groq LLM inference, Resend email dispatch, and DuckDuckGo discovery. Tests run locally against an isolated SQLite test database.

#### Rationale
- Zero external API costs and no rate limiting during tests.
- Millisecond test execution speeds enable continuous local development and reliable CI gating.
- Full offline test capability.

#### Consequences
- Tests do not verify live third-party network connectivity on every run.
- Changes to third-party API contracts must be updated in mock fixtures.

---

*Last updated: 2026-10-19*
