# Ruleset Deviations and Project Decisions

This file records intentional behavior decisions where design documents and implementation goals differ.

## D-001: Player count

- Decision: This project supports two-player couch play as a first-class mode.
- Source tension:
  - [AI/flip7-game-rules.md](AI/flip7-game-rules.md) describes the original game as 3+ players.
  - [AI/flip7-frontend-design-document.md](AI/flip7-frontend-design-document.md) targets two-player couch experience.
- Project behavior:
  - Backend permits 2-player games.
  - Frontend UX is optimized for two-player local play.
- Rationale:
  - Matches product direction for this implementation.

## D-002: Deck composition authority

- Decision: Use explicit house-rules deck composition from [AI/deck-composition-spec.md](AI/deck-composition-spec.md).
- Source tension:
  - Rules mention 94 cards without exact card-by-card counts.
- Project behavior:
  - Deck is seeded with project-authoritative counts and tested for total size.

## Update process

- Add new entries whenever implementation intentionally diverges from base source rules.
- Link each decision to the corresponding checklist or blocker item.
