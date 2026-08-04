# Flip 7 Deck Composition Spec (Project Authority)

This file defines the canonical deck composition for this implementation.

## Why this exists

- [AI/flip7-game-rules.md](AI/flip7-game-rules.md) states a 94-card deck.
- The exact per-card counts below are taken from the official Flip 7 rulebook.

## Canonical composition (94 cards)

### Number cards

- 0: 1 copy
- 1: 1 copy
- 2: 2 copies
- 3: 3 copies
- 4: 4 copies
- 5: 5 copies
- 6: 6 copies
- 7: 7 copies
- 8: 8 copies
- 9: 9 copies
- 10: 10 copies
- 11: 11 copies
- 12: 12 copies

Number-card subtotal: 79

### Modifier cards

- +2: 1 copy
- +4: 1 copy
- +6: 1 copy
- +8: 1 copy
- +10: 1 copy
- x2: 1 copy

Modifier subtotal: 6

### Action cards

- Freeze: 3 copies
- Flip Three: 3 copies
- Second Chance: 3 copies

Action subtotal: 9

Total cards: 79 + 6 + 9 = 94

## Implementation reference

- Backend seeding source of truth: [backend/game/services.py](backend/game/services.py)
- Constant name: DECK_COMPOSITION

## Change policy

- If a verified official composition is obtained, update this file first.
- Then update DECK_COMPOSITION and associated tests in the same change.
