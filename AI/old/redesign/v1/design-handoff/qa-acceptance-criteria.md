# QA and Acceptance Criteria

## Visual hierarchy

- [ ] The game board is visually dominant over setup or utility controls.
- [ ] The active player is unmistakable without reading small text.
- [ ] The primary next action is obvious in every state.
- [ ] Round, deck count, and target score are visible during play.
- [ ] Low, medium, high, and duplicate danger states are distinguishable.

## Functional states

- [ ] Setup supports player names, starting player, and target score.
- [ ] Create and Join controls have loading and disabled states.
- [ ] Both player panels show round score, total score, risk, and cards.
- [ ] Hit and Stay are always represented when legally available.
- [ ] Freeze Target and Flip Three Target appear only when available.
- [ ] Round summary reports each result and updated totals.
- [ ] Game over reports the winner, standings, and replay actions.

## Component quality

- [ ] Dynamic values are text/data, not baked into images.
- [ ] Cards are reusable variants rather than unique screenshots.
- [ ] Components use shared design tokens.
- [ ] No interface element is cropped from a reference sheet.
- [ ] Buttons include default, focus, pressed, disabled, and loading behavior.

## Responsive behavior

- [ ] The desktop landscape screen is readable at normal browser zoom.
- [ ] Two-column play remains legible at common laptop widths.
- [ ] Narrow screens stack panels and place the active player first.
- [ ] Actions remain visible and comfortably tappable.
- [ ] Modals fit without clipping or inaccessible controls.

## Accessibility

- [ ] All interactive controls are keyboard reachable.
- [ ] Focus indicators are clearly visible.
- [ ] Dialog focus is trapped and restored.
- [ ] Risk and status are not communicated through color alone.
- [ ] Action-result and turn changes have appropriate live announcements.
- [ ] Reduced-motion users do not receive essential information only through animation.

## Final visual comparison

- [ ] Setup resembles `references/04-setup-and-lobby.png` in hierarchy and atmosphere.
- [ ] Active play resembles `references/02-gameplay-components.png`.
- [ ] Controls resemble `references/03-controls-and-icons.png`.
- [ ] Cards follow `references/01-card-asset-sheet.png` without copying its errors.
- [ ] Overlays resemble `references/05-overlays-and-feedback.png`.
