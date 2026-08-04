# API Versioning and Compatibility Notes

## Versioning strategy

- Current API version label: v1.
- Strategy: URI-stable with additive evolution first.
- Non-breaking additions are preferred:
  - adding new fields to response payloads
  - adding new endpoints and action routes
- Breaking changes require one of:
  - introducing a v2 route namespace, or
  - content negotiation via explicit version header.

## Compatibility guarantees for v1

- Existing fields are not removed without a deprecation window.
- Existing error keys are stable:
  - error
  - error_code
  - details
- Action responses use a shared envelope for compatibility:
  - game_id
  - round_id
  - action_type
  - actor_player_id
  - target_player_id
  - next_turn_player_id
  - outcome
  - state

## Deprecation process

- Mark endpoint or field as deprecated in docs first.
- Keep deprecated behavior for at least one milestone.
- Add migration notes for frontend usage.
- Remove only after replacement path has shipped and passed tests.

## Consumer guidance

- Frontend should ignore unknown response fields.
- Frontend should key error handling on error_code and fall back to error text.
- Clients should not depend on ordering of object keys in JSON payloads.

## Test policy for compatibility

- Backend tests must include:
  - payload shape assertions for core actions
  - error shape assertions for invalid requests
  - regression tests for changed endpoint behavior
