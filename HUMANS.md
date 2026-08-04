# HUMANS.md — Notes from an AI-maximalist experiment

Flip 7 was built as an experiment in **AI-maximalist development**: the goal was to
lean on AI for as much of the work as possible — requirements, database design, API
design, implementation, tests, Dockerization, and UI iteration — and to observe where
that approach shines and where a human still needs to steer.

This file is the human's summary of what worked. The [`AI/`](AI/) folder holds the
artifacts that trail: the design documents, checklists, and iteration history the AI
and I produced along the way.

## What worked well

- **From rules to a working backend.** Given the game rules and requirements, AI was
  strong at producing a database schema and an API that implemented them. Writing API
  tests early gave quick confidence that the backend behaved.
- **Dockerizing the environment.** AI handled containerization well. Docker made it
  easy to spin the stack up and tear it back down while iterating.
- **Working from lists.** Breaking work into checklists and grinding through them was
  the single most effective workflow. Over the project this included an MVP checklist,
  a backend checklist, several frontend redesign checklists, a bug-bash checklist, and
  new-feature checklists.
- **A layered testing strategy.** Three kinds of tests each caught different problems:
  - *Requirement and game-rule tests* — the functional core.
  - *User-story tests as end-to-end tests* — protect against customer-experience
    regressions.
  - *Coverage tests* — catch code-level bugs by exercising all paths.

## Where the human had to steer

- **UI needs more than a prompt.** For the frontend, AI needed mockups of each screen
  plus a flow document describing how screens connect. Requirements and user stories
  were especially valuable here.
- **Manual testing before end-to-end tests.** Iterating and manually testing designs
  *before* asking AI to write end-to-end tests saved time and tokens — the design
  stabilizes first, then you lock it in with automated tests.
- **Upgrade the brain when stuck.** Switching to a larger, more capable model paid off
  on the hardest problems, which for this project were UI revisions and the bug bash.

## Process notes

- Run Docker first, then run end-to-end tests locally against it.
- Keep old AI documents separate from the current source of truth (hence
  [`AI/old/`](AI/old/) versus [`AI/truth/`](AI/truth/)).
- Create a test plan for each layer and work through it to completion.