---
name: transition-polish
description: >-
  Audit and maximize CSS transition coverage across all interactive and stateful UI elements.
  Use when polishing a React/web app for production-quality feel, after feature work is complete,
  or when the UI feels static, jarring, or unresponsive. Trigger keywords: transitions, animations,
  polish, smooth, jank, motion, easing, hover state, micro-interaction, perceived performance.
version: 1.0.0
author: Rishab Manocha
tags: [css, transitions, animations, ux, polish, accessibility]
---

# Transition Polish

Audit and maximize CSS transition coverage across all interactive, stateful, and
layered UI elements. Every state change the user can perceive must have a
purposeful, physically grounded transition — not for decoration, but as a
**cognitive aid** that preserves spatial orientation, confirms input, and masks
latency.

> "Great animations are invisible." — Emil Kowalski

## Authorities This Skill Draws From

- **Emil Kowalski** (animations.dev) — micro-mechanics of high-craft UI motion
- **Apple HIG / WWDC "Designing Fluid Interfaces"** — spring physics, interruptibility
- **Material Design 3** — duration tokens, easing curves, motion taxonomy
- **Josh Comeau** — `transition: all` anti-pattern, state-asymmetric transitions
- **Adam Argyle** (Chrome team / Open Props) — compositor-safe properties
- **Rachel Nabors** (*Animation at Work*) — cognitive science of motion, vestibular safety

---

## The Loop

Set up a **goal** to track this work, then iterate through every interactive
surface in the application.

### Phase 1: Discover Untransitioned Elements

Search for interactive and stateful elements that lack transitions:

```bash
# Find components with hover/active/focus states but no transition property
rg --pcre2 ':(hover|active|focus|focus-visible)' --glob '*.{css,scss,tsx,jsx}' -l | \
  xargs -I{} sh -c 'grep -L "transition" "{}" 2>/dev/null'

# Find conditional className toggling without transitions
rg --pcre2 'className.*\?' --glob '*.{tsx,jsx}' -l

# Find state-driven visibility toggling (show/hide without fade)
rg --pcre2 '(isOpen|isVisible|show|hidden|collapsed)\s*[?&|]' --glob '*.{tsx,jsx}' -l
```

### Phase 2: Apply Transitions by Element Category

For each file found, read it fully and apply the appropriate transition from the
tables below. Re-run the discovery commands after each batch; stop when no
untransitioned interactive elements remain.

---

## Duration & Easing Reference (Hard Rules)

### Duration Table

| Category | Duration | Examples |
| :--- | :--- | :--- |
| **Micro-Interactions** | **100–175ms** | Button `:hover`/`:active`, checkbox, toggle, icon highlight |
| **Small Entrances** | **150–250ms** | Tooltips, dropdowns, context menus, popovers |
| **Medium Overlays** | **250–350ms** | Modals, bottom sheets, navigation drawers, sidebars |
| **Large Transforms** | **350–500ms** | Expanding card → full page, route transitions |
| **Exit Animations** | **20–35% faster than entrance** | Closing modals, dismissing toasts, collapsing menus |

### Hard Ceilings

- **Sub-100ms:** Perceived as instantaneous. Hover/active must initiate here.
- **300ms:** Standard baseline for general UI transitions.
- **500ms:** Hard ceiling for any interaction-driven transition.
- **1000ms:** Absolute maximum. Beyond this, it's an involuntary loading screen.

### Easing Curves

| Motion Type | Easing | Curve |
| :--- | :--- | :--- |
| **Entrances** (into viewport) | Decelerate / Ease-Out | `cubic-bezier(0.0, 0.0, 0.2, 1)` |
| **Exits** (out of viewport) | Accelerate / Ease-In | `cubic-bezier(0.4, 0.0, 1, 1)` |
| **On-Screen Movement** (A→B) | Standard / Ease-In-Out | `cubic-bezier(0.2, 0.0, 0.0, 1.0)` |
| **Sheet/Drawer (iOS-like)** | Custom Decel | `cubic-bezier(0.32, 0.72, 0, 1)` |

---

## Property Safety (Performance Hard Rules)

### ✅ GPU-Safe (Compositor-Only) — Always Use These

- `transform` (`translate`, `scale`, `rotate`)
- `opacity`
- `filter` (with care)
- `clip-path` (with care)

### ❌ NEVER Animate These Directly

- `width`, `height`, `top`, `left`, `right`, `bottom` → Use `transform: translate()`
- `margin`, `padding`, `border-width` → Use `transform: scale()` or grid tricks
- `box-shadow` → Use a `::after` pseudo-element with pre-rendered shadow, transition its `opacity`

### Workarounds

**Accordion expand/collapse** — Use CSS Grid instead of animating `height`:
```css
.accordion-content {
  display: grid;
  grid-template-rows: 0fr;
  transition: grid-template-rows 250ms ease-out;
}
.accordion-content[data-open="true"] {
  grid-template-rows: 1fr;
}
.accordion-inner {
  overflow: hidden;
}
```

---

## Anti-Patterns (Zero Tolerance)

### 1. `transition: all`
**Never use `transition: all`.** It forces the browser to evaluate every
animatable property on every paint tick, triggers unintended transitions on
resize/reflow, and is impossible to debug.

**Always explicitly declare properties:**
```css
/* ❌ WRONG */
transition: all 200ms ease;

/* ✅ CORRECT */
transition: transform 200ms ease-out, opacity 200ms ease-out;
```

### 2. Entry Scale from Zero
Scaling from `scale(0)` to `scale(1)` looks cartoonish. Use subtle entry scales:
```css
/* ❌ WRONG */
.modal { transform: scale(0); }
.modal.open { transform: scale(1); }

/* ✅ CORRECT */
.modal {
  transform: scale(0.95);
  opacity: 0;
}
.modal.open {
  transform: scale(1);
  opacity: 1;
}
```

### 3. Symmetric Enter/Exit Timing
Exit must always be **faster** than entrance. The user has made their decision;
get out of the way.
```css
.sheet {
  /* Exit: fast */
  transition: transform 200ms cubic-bezier(0.4, 0, 1, 1);
}
.sheet.open {
  /* Entrance: deliberate */
  transition: transform 300ms cubic-bezier(0.32, 0.72, 0, 1);
}
```

### 4. Center-Origin Scaling
Dropdowns, context menus, and popovers must scale from their **trigger element**,
not from their geometric center:
```css
.dropdown[data-side="bottom"] { transform-origin: top left; }
.dropdown[data-side="top"] { transform-origin: bottom left; }
```

### 5. Animation Tax
If the API responds in 50ms but you force an unskippable 600ms animation,
you're holding the user hostage. **Animation must never make a fast system
feel slower.**

---

## Accessibility: `prefers-reduced-motion` (Mandatory)

~35% of adults over 40 have motion sensitivity. This is a safety requirement,
not an optional preference.

**Do NOT strip all motion.** Replace spatial displacement with opacity fades:

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }

  /* Preserve gentle opacity for context */
  .modal-overlay, .dropdown, .toast, .tooltip {
    transition: opacity 150ms ease-out !important;
    transform: none !important;
  }
}
```

### What NOT to Animate (Regardless of Preference)

- Text input focus / typing cursor
- Table row selection during rapid multi-check
- Standard text hyperlinks (underline transitions > 100ms)
- Parallax scrolling, infinite spinners dominating the viewport
- Continuous pulsing / breathing icons (WCAG 2.2.2 violation)

---

## Element-by-Element Checklist

Work through each category. For every element, confirm it has an appropriate
transition. If not, add one.

### Interactive Controls
- [ ] Buttons: `background-color`, `transform: scale()` on `:active` (100–150ms, ease-out)
- [ ] Icon buttons: `opacity`, `transform: scale()` (100ms)
- [ ] Checkboxes/radios: check mark `opacity` + `transform: scale()` (100–150ms)
- [ ] Toggle switches: thumb `transform: translateX()` (150ms, ease-out)
- [ ] Tabs: active indicator `transform: translateX()` + `width` via scale (200ms)
- [ ] Links/nav items: `color`, `opacity` (100ms)

### Disclosure & State Changes
- [ ] Accordions: `grid-template-rows` (250ms, ease-out)
- [ ] Collapsible sidebars: `transform: translateX()` (250ms)
- [ ] Disclosure triangles: `transform: rotate()` (150ms)
- [ ] Tab panels: `opacity` cross-fade (200ms)

### Overlays & Layers
- [ ] Modal dialogs: backdrop `opacity` (200ms) + content `transform: scale(0.95→1)` + `opacity` (250ms)
- [ ] Bottom sheets: `transform: translateY()` (300ms entrance, 200ms exit)
- [ ] Dropdowns/menus: `opacity` + `transform: scale(0.95→1)` from trigger origin (200ms)
- [ ] Tooltips: `opacity` (150ms delay-in, 0ms delay-out)
- [ ] Toasts/snackbars: `transform: translateY()` + `opacity` (250ms in, 150ms out)
- [ ] Popovers: `opacity` + `transform` from trigger (200ms)

### Loading & Async States
- [ ] Skeleton screens: shimmer gradient animation (1.5s linear infinite)
- [ ] Progress bars: `width` via `transform: scaleX()` (300ms)
- [ ] Spinner → content swap: `opacity` cross-fade (200ms)

### Layout & Data
- [ ] Drag-and-drop reorder: items `transform: translateY()` (200ms)
- [ ] Filter/sort grid: item `opacity` + `transform` (250ms)
- [ ] Card expand → full view: container transform (350–500ms)

---

## State-Asymmetric Transitions Pattern

Hover-on should feel snappy; hover-off should feel smooth:

```css
.button {
  transform: translateY(0);
  transition: transform 250ms ease-out; /* Slow return to rest */
}
.button:hover {
  transform: translateY(-2px);
  transition: transform 100ms ease-out; /* Instant reaction */
}
```

---

## Verification

After completing all categories:

```bash
# 1. Search for remaining interactive elements without transitions
rg --pcre2 ':(hover|active|focus)' --glob '*.{css,scss,tsx}' -l | \
  xargs -I{} sh -c 'grep -L "transition" "{}"'

# 2. Search for `transition: all` violations
rg 'transition:\s*all' --glob '*.{css,scss,tsx}'

# 3. Search for layout-triggering property animations
rg --pcre2 'transition:.*\b(width|height|top|left|right|bottom|margin|padding)\b' --glob '*.{css,scss}'

# 4. Confirm prefers-reduced-motion is implemented
rg 'prefers-reduced-motion' --glob '*.{css,scss}'

# 5. Build and lint
npm run build && npm run lint
```

All 5 checks must pass before the skill is complete.
