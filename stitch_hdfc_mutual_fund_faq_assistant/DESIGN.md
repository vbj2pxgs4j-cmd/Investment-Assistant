---
name: Luminous Fintech
colors:
  surface: '#0b1326'
  surface-dim: '#0b1326'
  surface-bright: '#31394d'
  surface-container-lowest: '#060e20'
  surface-container-low: '#131b2e'
  surface-container: '#171f33'
  surface-container-high: '#222a3d'
  surface-container-highest: '#2d3449'
  on-surface: '#dae2fd'
  on-surface-variant: '#bacac1'
  inverse-surface: '#dae2fd'
  inverse-on-surface: '#283044'
  outline: '#85948c'
  outline-variant: '#3c4a43'
  surface-tint: '#2fe0aa'
  primary: '#44edb7'
  on-primary: '#003828'
  primary-container: '#00d09c'
  on-primary-container: '#00533c'
  inverse-primary: '#006c4f'
  secondary: '#adc6ff'
  on-secondary: '#002e6a'
  secondary-container: '#0566d9'
  on-secondary-container: '#e6ecff'
  tertiary: '#ffc98a'
  on-tertiary: '#472a00'
  tertiary-container: '#fda417'
  on-tertiary-container: '#673f00'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#59fdc5'
  primary-fixed-dim: '#2fe0aa'
  on-primary-fixed: '#002116'
  on-primary-fixed-variant: '#00513b'
  secondary-fixed: '#d8e2ff'
  secondary-fixed-dim: '#adc6ff'
  on-secondary-fixed: '#001a42'
  on-secondary-fixed-variant: '#004395'
  tertiary-fixed: '#ffddb8'
  tertiary-fixed-dim: '#ffb95f'
  on-tertiary-fixed: '#2a1700'
  on-tertiary-fixed-variant: '#653e00'
  background: '#0b1326'
  on-background: '#dae2fd'
  surface-variant: '#2d3449'
typography:
  display-lg:
    fontFamily: Outfit
    fontSize: 48px
    fontWeight: '700'
    lineHeight: 56px
    letterSpacing: -0.02em
  display-lg-mobile:
    fontFamily: Outfit
    fontSize: 32px
    fontWeight: '700'
    lineHeight: 40px
    letterSpacing: -0.02em
  headline-md:
    fontFamily: Outfit
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
  title-sm:
    fontFamily: Plus Jakarta Sans
    fontSize: 18px
    fontWeight: '600'
    lineHeight: 24px
  body-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  body-sm:
    fontFamily: Plus Jakarta Sans
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  label-caps:
    fontFamily: Plus Jakarta Sans
    fontSize: 12px
    fontWeight: '700'
    lineHeight: 16px
    letterSpacing: 0.05em
  mono-data:
    fontFamily: JetBrains Mono
    fontSize: 14px
    fontWeight: '500'
    lineHeight: 20px
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  base: 4px
  xs: 8px
  sm: 16px
  md: 24px
  lg: 40px
  xl: 64px
  gutter: 20px
  margin-mobile: 16px
  margin-desktop: 48px
---

## Brand & Style

This design system is built for the modern investor, blending the clarity of high-end fintech with a sophisticated, dark-mode-first aesthetic. The personality is precise, trustworthy, and technologically advanced. 

The visual direction combines **Minimalism** with **Glassmorphism**. High-contrast typography ensures readability against deep slate backgrounds, while emerald accents provide a "digital-first" energy. The use of translucency and 1px borders creates a sense of layered physical depth, mimicking high-end hardware interfaces. The emotional goal is to make the user feel secure yet empowered by data.

## Colors

The palette is anchored in a dark-mode hierarchy to reduce eye strain during long analytical sessions.

- **Primary (Emerald):** Used for growth indicators, primary actions, and success states. It represents the "Go" signal in financial contexts.
- **Secondary (Security Blue):** Dedicated to PII (Personally Identifiable Information), security settings, and verification badges to evoke stability and institutional trust.
- **Tertiary (Amber):** Reserved for warnings, pending states, or market volatility alerts.
- **Neutrals:** A range of slates. `#0B0F17` serves as the canvas, while `#0F172A` acts as the surface layer for cards and containers.

## Typography

The system utilizes **Outfit** for headlines to provide a modern, geometric character that feels premium and clean. **Plus Jakarta Sans** is used for body copy and UI labels due to its exceptional legibility at smaller scales and slightly warmer tone, which balances the coldness of the dark slate.

Numerical data should prioritize the "mono-data" style when appearing in tables or stock tickers to ensure alignment and rapid scanning of fluctuating values.

## Layout & Spacing

The layout follows a **Fluid Grid** model with a focus on internal containment. 
- **Desktop:** 12-column grid, max-width 1440px.
- **Tablet:** 8-column grid.
- **Mobile:** 4-column grid.

Spacing follows a strict 4px base unit. Card internal padding should be consistently `md` (24px) for desktop and `sm` (16px) for mobile to maximize content density. Use wide margins (`xl`) between major sections to allow the glassmorphic effects and background depth to breathe.

## Elevation & Depth

Hierarchy is achieved through **Glassmorphism** and tonal stacking rather than heavy shadows.

1.  **Level 0 (Base):** Deepest Slate (`#0B0F17`).
2.  **Level 1 (Cards/Surfaces):** `#0F172A` with a 1px border of `#334155`.
3.  **Level 2 (Modals/Overlays):** Translucent background (Alpha 60%), `backdrop-blur: 16px`, and a subtle outer glow using the primary emerald color at 5% opacity.

The "neon glow" effect is reserved for the active state of cards or featured portfolio items, achieved with a `0px 0px 20px 0px` spread of the primary color at very low alpha (10-15%).

## Shapes

The design system uses a **Rounded** (Level 2) approach to soften the technical edge of the fintech space.
- **Buttons & Small Inputs:** 0.5rem (8px).
- **Cards & Large Containers:** 1rem (16px).
- **Selection Chips:** Pill-shaped (full radius) to distinguish them from actionable buttons.

## Components

### Buttons
- **Primary:** Solid Emerald (`#00D09C`) with dark slate text. No gradient. High contrast is key.
- **Secondary:** Ghost style. 1px border (`#334155`) with Emerald text. Background becomes 5% Emerald on hover.

### Cards
Cards are the primary container. They must have a 1px solid border (`#334155`). For "active" or "highlighted" financial products, apply a subtle top-down linear gradient (10% Emerald to Transparent) to the border only.

### Input Fields
Inputs use the Level 1 surface color. On focus, the border transitions from slate to Emerald, and a subtle 4px emerald outer glow is applied. Labels should use the `label-caps` typography style.

### Chips & Tags
Used for stock categories or asset classes. High-growth assets use Emerald tints; volatile assets use Amber. All chips are pill-shaped with a 10% opacity background of their respective semantic color.

### Data Visualizations
Charts should utilize the primary Emerald for "Up" trends and a custom soft Red for "Down" trends. Grid lines in charts should be kept at 5% opacity to maintain a clean, glassmorphic look.