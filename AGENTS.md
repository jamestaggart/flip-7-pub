# AGENTS.md

## Project workflow

- Use the Docker environment for all backend, database, API, and service work.
- Use Docker for migrations, Django management commands, and backend testing.
- For frontend end-to-end tests, run Playwright locally on the host machine with the local Node/npm environment, not inside Docker.
- Never run Playwright or browser-based end-to-end tests inside Docker containers; use the host machine and the local browser so the UI is accessible during test runs.
- Keep the frontend test environment aligned with the local browser and local dev server so the UI is accessible during test runs.
- Keep the development environment consistent with the containerized setup for backend services while using local host execution for browser-based validation.

## Project context

- This project is a Flip 7 game built with PostgreSQL, Django REST Framework, Next.js, and Playwright.
- The implementation should follow the design documents in the AI folder.
- Prefer using the Docker Compose environment for development and verification.

## Reference documents

- Rules and game definition: [AI/flip7-game-rules.md](AI/flip7-game-rules.md)
- Game design direction: [AI/flip7-game-design-document.md](AI/flip7-game-design-document.md)
- 4NF database schema: [AI/flip7-database-schema.md](AI/flip7-database-schema.md)
- API design: [AI/flip7-api-design.md](AI/flip7-api-design.md)
- API test plan: [AI/flip7-api-test-plan.md](AI/flip7-api-test-plan.md)
- Frontend design document: [AI/flip7-frontend-design-document.md](AI/flip7-frontend-design-document.md)
- Frontend test plan: [AI/flip7-frontend-test-plan.md](AI/flip7-frontend-test-plan.md)
- Implementation roadmap: [AI/implementation-plan.md](AI/implementation-plan.md)
