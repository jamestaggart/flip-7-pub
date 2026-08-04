# Design System

## Design principles

- Warm, tactile digital tabletop rather than dashboard UI.
- Readable from several feet away on a shared landscape screen.
- Playful and dramatic without becoming childish or visually noisy.
- One dominant focus per state: current turn, result, or next action.
- Dynamic content remains text and components, never baked into images.

## Color tokens

```css
:root {
  --surface-page: #07131f;
  --surface-board: #0d2030;
  --surface-panel: #f1e7d5;
  --surface-panel-dark: #101b26;
  --surface-overlay: rgba(3, 10, 18, 0.82);

  --ink-primary: #f8f1e4;
  --ink-dark: #102235;
  --ink-muted: #aeb9c3;

  --gold-500: #d99b2b;
  --gold-300: #f2c55d;
  --blue-500: #167ac6;
  --blue-300: #55bfff;
  --green-500: #4e9f31;
  --green-300: #8fd44c;
  --red-500: #bd382d;
  --red-300: #ff695d;
  --purple-500: #6d318f;
  --purple-300: #b272db;
  --orange-500: #d76421;

  --risk-low: #67ba3a;
  --risk-medium: #e6a51f;
  --risk-high: #d64035;

  --border-subtle: rgba(242, 197, 93, 0.35);
  --shadow-panel: 0 12px 30px rgba(0, 0, 0, 0.34);
  --glow-active: 0 0 0 2px #55bfff, 0 0 26px rgba(85, 191, 255, 0.65);
  --glow-danger: 0 0 0 2px #ff695d, 0 0 24px rgba(255, 105, 93, 0.55);
}
```

These values are implementation starting points. Tune them while visually comparing against the references.

## Typography

Use a bold, condensed display face for headings and actions and a highly readable sans serif for body text. Suggested freely available substitutes:

- Display: `Roboto Condensed`, `Barlow Condensed`, or `Oswald`.
- UI/body: `Inter`, `Source Sans 3`, or system sans serif.

Minimum shared-screen sizes:

- Game title: 40–56 px.
- Turn banner: 28–38 px.
- Player name: 26–34 px.
- Primary score: 36–52 px.
- Primary button label: 24–32 px.
- Supporting text: 16–20 px.

## Spacing and sizing

Use an 8 px spacing system. Prefer 16, 24, 32, and 48 px gaps. Primary actions should be at least 72 px tall on desktop. Clickable targets must be at least 44 × 44 px.

## Shape language

- Main panels: 20–28 px radius.
- Buttons: 12–18 px radius.
- Cards: 10–14 px radius.
- Pills: full or 999 px radius.
- Use thin gold outlines and layered inner borders sparingly.

## Elevation

Use three levels:

1. Board surface.
2. Player and utility panels.
3. Active controls, banners, and modals.

Avoid excessive shadows. Active focus should come from outline, glow, scale, and contrast rather than blur alone.

## Motion guidance

- Card draw: 220–320 ms slide/flip.
- Turn change: 180–250 ms crossfade and glow transfer.
- Banner feedback: 200 ms entrance, 1–2 second hold when nonblocking.
- Modal: 180–240 ms scale/fade.
- Respect reduced-motion preferences.
