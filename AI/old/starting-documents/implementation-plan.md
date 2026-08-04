# Flip 7 Implementation Plan

This plan turns the design documents into a build roadmap for completing the full project.

## 1. Project Goals

Build a working Flip 7 game with:
- PostgreSQL database
- Django REST API
- Next.js frontend
- Playwright end-to-end tests
- API and frontend test coverage aligned to the design documents

## 2. Delivery Phases

### Phase 1 — Foundation
- Finalize project structure
- Confirm Docker and environment setup
- Validate backend and frontend boot process
- Ensure database connectivity works

### Phase 2 — Database Implementation
- Implement the full PostgreSQL schema from the 4NF design
- Add migrations for players, games, rounds, turns, cards, and locations
- Seed initial card definitions and deck data
- Add validation rules for game state consistency

### Phase 3 — Backend API Implementation
- Implement endpoints for:
  - players
  - games
  - rounds
  - turns
  - decks and cards
  - hit and stay actions
  - busts and Flip 7 resolution
  - modifiers and action cards
  - scoring and results
- Add rule-enforcement logic in the backend service layer
- Add serializer validation and error handling
- Add API tests for each endpoint and rule

### Phase 4 — Frontend Implementation
- Build the home screen and game setup flow
- Build the main game board UI
- Implement turn-based gameplay with hit/stay controls
- Render cards, scores, action effects, and round summaries
- Connect the frontend to the backend API

### Phase 5 — Testing and Verification
- Implement frontend user-story tests in Playwright
- Implement API tests for rule coverage
- Run the full test suite
- Fix issues and confirm the game works end to end

### Phase 6 — Execution and Polish
- Add UI polish and animations
- Add loading/error states
- Improve rules clarity and game feedback
- Prepare for local run and demo

## 3. Build Order

1. Database models and migrations
2. API endpoints and rule service
3. Frontend UI shell
4. API integration
5. End-to-end tests
6. Bug fixes and refinements

## 4. Success Criteria

The project is complete when:
- a two-player game can be created and played locally
- the backend enforces the core game rules
- the frontend displays the game state clearly
- the API and frontend tests pass
- the game can be run using Docker

## 5. Immediate Next Steps

- Implement the database schema in Django migrations
- Create the initial API endpoints for game creation and player joining
- Build the first frontend game screen
- Add Playwright smoke tests for game start and turn flow
