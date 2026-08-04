# The `AI/` folder — artifact trail of an AI-maximalist experiment

Flip 7 was built as an experiment in AI-maximalist development (see [HUMANS.md](../HUMANS.md)
for the human's findings). This folder is the **artifact trail**: the design documents,
requirements, checklists, and iteration history that the AI and the human produced while
building the game. It is intentionally preserved rather than polished away — the value of
the experiment is in showing *how* the project was designed and iterated, not just the
final result.

If you only want to run or read the game, you do not need anything here — start with the
root [README](../README.md) and [docs/](../docs/).

## How it is organized

- **[`truth/`](truth/)** — the current source of truth. Documents here reflect the game
  as it actually is today.
  - [`flip7-requirements.md`](truth/flip7-requirements.md) — the authoritative
    requirements and rules the implementation follows.
  - [`public-release-work/`](truth/public-release-work/) — notes and checklists from
    preparing the project for public release.
- **[`old/`](old/)** — historical iteration artifacts. These captured the state of the
  project at various points and are kept for provenance. They may be out of date and
  should not be treated as current.
  - `starting-documents/` — the initial design set (rules, schema, API design, test
    plans) that bootstrapped the build.
  - `redesign/`, `feature-requests/`, `new-features/` — successive iteration passes on
    the UI and features.
  - `bug-bash/`, `test-plan/` — the QA and coverage passes.

## How to read it

Treat `truth/` as canonical and `old/` as history. When the two disagree, `truth/` and the
actual code win.
