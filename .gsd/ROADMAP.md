---
milestone: Testing & Hardening
version: 1.0.0
updated: 2026-10-19T14:48:00Z
---

# Roadmap

> **Current Phase:** Phase 1: Test Infrastructure & Mock Services
> **Status:** ⬜ Not Started

## Must-Haves (from SPEC)

- [ ] Automated pytest test framework configured and runnable
- [ ] Mock fixtures implemented for Groq LLM, Resend email, and DuckDuckGo discovery
- [ ] Database CRUD and event timeline tests passing with SQLite fallback
- [ ] All FastAPI endpoints covered by automated unit/integration tests
- [ ] Scraper service hardened against network timeouts, invalid URLs, and missing contacts

---

## Phases

### Phase 1: Test Infrastructure & Mock Services
**Status:** 🔄 In Progress
**Objective:** Establish the testing environment with pytest, fixtures, and mocked third-party services so tests run completely offline and deterministically.
**Requirements:** REQ-01, REQ-02

**Plans:**
- [ ] Plan 1.1: Pytest configuration, dependencies, and test database harness
- [ ] Plan 1.2: Deterministic mock fixtures for Groq LLM, Resend, and DuckDuckGo

---

### Phase 2: Database & Data Access Layer Tests
**Status:** ⬜ Not Started
**Objective:** Verify data persistence, JSON serialization, event timeline logging, and CRUD consistency under normal and edge conditions.
**Requirements:** REQ-03
**Depends on:** Phase 1

**Plans:**
- [ ] Plan 2.1: Lead CRUD operations, JSON field serialization, and validation tests
- [ ] Plan 2.2: Lead event timeline creation and cascade deletion tests

---

### Phase 3: API Endpoint Test Suite
**Status:** ⬜ Not Started
**Objective:** Provide comprehensive request/response test coverage across all FastAPI API routes.
**Requirements:** REQ-04
**Depends on:** Phase 1, Phase 2

**Plans:**
- [ ] Plan 3.1: Health check, company analysis initiation, and validation tests
- [ ] Plan 3.2: Review approval queue, email dispatch, and dashboard metric tests

---

### Phase 4: Scraper Resilience Hardening & Pipeline Verification
**Status:** ⬜ Not Started
**Objective:** Harden scraper routines against timeouts, anti-bot blocking, and missing contact emails, and verify end-to-end pipeline execution with mocks.
**Requirements:** REQ-05
**Depends on:** Phase 1, Phase 2, Phase 3

**Plans:**
- [ ] Plan 4.1: Scraper error handling, retry backoff, and contact extraction hardening
- [ ] Plan 4.2: End-to-end pipeline orchestration and error recovery test
