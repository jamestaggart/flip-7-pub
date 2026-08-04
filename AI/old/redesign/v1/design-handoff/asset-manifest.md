# Asset Manifest

## Asset strategy

The reference sheets define visual direction. They are not spritesheets and must not be cropped into production UI elements. Most interface elements should be built with HTML/CSS, canvas, or native UI components.

## Production assets recommended

| Path | Format | Purpose | Required for initial build |
|---|---|---|---|
| `assets/branding/flip7-logo.svg` | SVG | Clean game logo | No; text placeholder works |
| `assets/branding/flip7-logo-compact.svg` | SVG | Header/mobile mark | No |
| `assets/decorative/flip7-burst.webp` | WebP/PNG | Seven-card bonus celebration | No |
| `assets/decorative/confetti.webp` | WebP/PNG | Game-over decoration | No |
| `assets/decorative/crown.svg` | SVG | Winner icon | No; icon substitute works |
| `assets/textures/tabletop.webp` | WebP | Subtle board texture | No; CSS gradient works |
| `assets/textures/paper.webp` | WebP | Optional card/panel texture | No; CSS texture works |
| `assets/icons/*.svg` | SVG | Custom icon set | No; use Lucide/Phosphor initially |

## Code-generated components

Do not request image exports for:

- Number, modifier, or action cards.
- Buttons and button states.
- Player panels.
- Status pills.
- Score badges.
- Risk meters.
- Inputs and selectors.
- Tables and lobby rows.
- Modal frames.
- Banners.
- Dynamic player names, scores, round data, or deck data.

## Temporary icon mapping

Use a consistent open-source icon library until custom exports exist:

- Player: user/person.
- Winner: crown/trophy.
- Deck: cards/layers.
- Target score: target.
- Round: calendar/hash.
- Menu: menu.
- Warning: triangle-alert.
- Freeze: snowflake.
- Flip Three: layers-three/cards.
- Second Chance: heart.
- Bust: burst/x-octagon.
- Help: circle-help.

## Asset export requirements

Final artwork should have transparent backgrounds, no embedded UI labels, no baked player names or scores, and no unnecessary empty canvas. Export 1× and 2× raster versions. Preserve source SVG/Figma files.
