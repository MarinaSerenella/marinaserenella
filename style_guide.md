# Style Guide - Marina Serenella

This style guide outlines the design system, colors, typography, components, and layout spacing defined in `assets/css/style.css`.

---

## 1. Color Palette

The project uses CSS custom properties defined in `:root` for color tokens.

### Theme Colors
*   **Deep Navy (Primary Theme)**: `var(--blue-950)` -> `#06213f`
*   **Royal Navy**: `var(--blue-900)` -> `#082b52`
*   **Ocean Blue**: `var(--blue-800)` -> `#0f3d6f`
*   **Sky Accent Blue**: `var(--blue-700)` -> `#155a92`
*   **Teal/Cyan (Call to Action)**: `var(--cyan-500)` -> `#35b7cf`

### Neutral Colors
*   **Light Sand Background**: `var(--sand-50)` -> `#fbf7ef` (Used on `.section.alt`)
*   **Warm Sand Accent**: `var(--sand-100)` -> `#f3eadb`
*   **Ice Blue Highlight**: `var(--blue-100)` -> `#e7f2fb` (Used for hover states, select menus, tags)
*   **Ink Black (Body Text)**: `var(--ink)` -> `#172334`
*   **Muted Gray**: `var(--muted)` -> `#657184`
*   **White**: `var(--white)` -> `#ffffff`

### Utility Colors
*   **Borders/Lines**: `var(--line)` -> `rgba(6, 33, 63, 0.12)`
*   **Shadows**: `var(--shadow)` -> `0 18px 55px rgba(6, 33, 63, 0.13)`

---

## 2. Typography

*   **Font Family**: `system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif`
*   **Base Line Height**: `1.6`
*   **Headings**:
    *   **H1 (Hero Heading)**: Font size dynamically scales via `clamp(2.35rem, 6vw, 5rem)`, line-height `0.98`, letter-spacing `-0.05em`, color `var(--white)`.
    *   **H2 (Section Heading)**: Font size dynamically scales via `clamp(1.95rem, 4vw, 3.15rem)`, line-height `1.05`, letter-spacing `-0.035em`, color `var(--blue-950)`.
    *   **H3 (Card/Sub Headings)**: Font size `1.28rem`, line-height `1.2`, color `var(--blue-950)`.
*   **Body / Lead Text**:
    *   **Lead Paragraph**: Font size scales via `clamp(1.05rem, 2vw, 1.35rem)`, color `rgba(255,255,255,.86)` (on dark heroes).
    *   **Standard Paragraph**: `margin: 0 0 1rem;`
*   **Labels & Indicators**:
    *   **Kicker (Subtitle above Heading)**: `display: block; margin-bottom: 0.6rem; color: var(--blue-700); font-weight: 900; text-transform: uppercase; letter-spacing: .12em; font-size: .78rem;`
    *   **Eyebrow**: Inline rounded capsule (`display: inline-flex`), background `rgba(255,255,255,.12)`, border `1px solid rgba(255,255,255,.28)`, padding `.35rem .7rem`, font-weight `800`, font-size `.92rem`.

---

## 3. UI Buttons & Interaction

All buttons share core structural properties:
*   **Height**: Min-height of `48px`
*   **Padding**: `.78rem 1.05rem`
*   **Border Radius**: `999px` (fully rounded capsule)
*   **Typography**: Font weight `800`, letter spacing `.01em`
*   **Transition**: `transform .15s ease, box-shadow .15s ease, background .15s ease`
*   **Hover Effect**: `transform: translateY(-1px); box-shadow: 0 10px 28px rgba(6, 33, 63, .18);`

### Button Variants
1.  **Primary Button** (`.btn-primary`): Background `var(--cyan-500)`, text color `var(--blue-950)`.
2.  **Dark Button** (`.btn-dark`): Background `var(--blue-950)`, text color `var(--white)`.
3.  **Light Button** (`.btn-light`): Background `var(--white)`, text color `var(--blue-950)`.
4.  **Outline Button** (`.btn-outline`): Background `transparent`, text color `var(--white)`, border `1px solid rgba(255,255,255,.55)`.

---

## 4. Cards & Containers

*   **Max Page Container Width**: `1180px` (with `calc(100% - 2rem)` safety bounds on mobile viewports).
*   **Border Radii**:
    *   **Large Corners (`--radius-lg`)**: `28px` (used on standard content cards, image frames, and media panels).
    *   **Medium Corners (`--radius-md`)**: `18px` (used for stat badges inside the hero section).
*   **Card Box Shadows**: `0 10px 32px rgba(6, 33, 63, .07)` (provides a premium, soft elevated appearance).
