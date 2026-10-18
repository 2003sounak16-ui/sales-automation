# Contributing to SalesFlow Automation Hub

Thank you for your interest in contributing to SalesFlow Automation Hub!

## Development Workflow

1. **Fork the repository** and clone your fork locally.
2. **Create a branch** for your feature or bug fix:
   ```bash
   git checkout -b feature/my-new-feature
   ```
3. **Set up the environments**:
   - Backend: Python 3.11 with FastAPI (see [Backend Setup](README.md#2-backend-setup))
   - Frontend: Node.js 18+ with Next.js (see [Frontend Setup](README.md#3-frontend-setup))
4. **Verify your changes**:
   - Run frontend linter: `cd frontend && npm run lint`
   - Verify backend runs locally: switch to backend (`cd ../backend` or from root `cd backend`) and run `uvicorn main:app --reload`
   *(Note: Automated test suites are currently in progress and not yet configured)*.
5. **Open a Pull Request**:
   - Provide a concise description of your changes.
   - Wait for automated code analysis and reviews.

## Code Standards
- Follow PEP 8 guidelines for Python backend code.
- Ensure ESLint checks pass for the frontend (`npm run lint`).
