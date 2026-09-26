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

Audit and enforce CSS transitions across interactive, stateful, and layered UI elements.

## Workflow

### 1. Discovery
Find untransitioned interactive states and conditional renderings:

```bash
# Find hover/active/focus styles without transition declarations
rg --pcre2 ':(hover|active|focus|focus-visible)' --glob '*.{css,scss,tsx,jsx}' -l | \
  xargs -I{} sh -c 'grep -L "transition" "{}" 2>/dev/null'

# Find dynamic className or visibility toggles lacking transitions
rg --pcre2 'className.*\?' --glob '*.{tsx,jsx}' -l
rg --pcre2 '(isOpen|isVisible|show|hidden|collapsed)\s*[?&|]' --glob '*.{tsx,jsx}' -l
```

### 2. Apply Transitions

#### Durations & Curves

| Category | Duration | Curve | Examples |
| :--- | :--- | :--- | :--- |
| **Micro-Interactions** | 100–175ms | `cubic-bezier(0, 0, 0.2, 1)` | Buttons, checkboxes, toggles, icon states |
| **Small Entrances** | 150–250ms | `cubic-bezier(0, 0, 0.2, 1)` | Tooltips, dropdowns, popovers |
| **Overlays / Sheets** | 250–350ms (in) / 150–200ms (out) | `cubic-bezier(0.32, 0.72, 0, 1)` | Modals, bottom sheets, navigation drawers |
| **Large Transforms** | 350–500ms | `cubic-bezier(0.2, 0, 0, 1)` | Expanding cards, route transitions |

*Exits must always be 20–35% faster than entrances.*

#### Compositor Safety

- ✅ **Allowed (GPU-composited):** `transform`, `opacity`
- ❌ **Prohibited:** `width`, `height`, `top`, `left`, `right`, `bottom`, `margin`, `padding`, `border-width`

*For height expand/collapse, use CSS Grid:*
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

## Anti-Patterns

| ❌ Anti-Pattern | ✅ Correct Pattern |
| :--- | :--- |
| `transition: all 200ms ease;` | `transition: transform 200ms ease-out, opacity 200ms ease-out;` |
| `transform: scale(0)` to `scale(1)` | `transform: scale(0.95)` with `opacity: 0` to `scale(1)` with `opacity: 1` |
| Center-origin popovers | `transform-origin: top left` (anchored to trigger) |
| Symmetrical modal close | Fast exit: `200ms cubic-bezier(0.4, 0, 1, 1)` vs `300ms` entry |

### State-Asymmetric Hover Pattern

Snappy hover-in, smooth hover-out, guarded for touch devices:

```css
.button {
  transform: translateY(0);
  transition: transform 250ms ease-out;
}

@media (hover: hover) and (pointer: fine) {
  .button:hover {
    transform: translateY(-2px);
    transition: transform 100ms ease-out;
  }
}
```

## Accessibility (`prefers-reduced-motion`)

Do not remove transitions entirely (`none !important`). Substitute displacement with an opacity fade:

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }

  .modal-overlay, .dropdown, .toast, .tooltip {
    transition: opacity 150ms ease-out !important;
    transform: none !important;
  }
}
```

### Prohibited Animations (All Users)
- Typing cursor movements or text input focus borders
- Table row multi-selection
- Parallax scrolling
- Infinite looping pulses/spinners (WCAG 2.2.2)

## Checklist

- [ ] Interactive controls: button active scale (100–150ms), toggle translate (150ms), tab switch (200ms)
- [ ] Overlays: backdrop opacity (200ms), modal content scale/fade (250ms in, 180ms out)
- [ ] Dropdowns: opacity + scale(0.95→1) from trigger origin (200ms)
- [ ] Tooltips: opacity (150ms delay-in, 0ms delay-out)
- [ ] Zero `transition: all` declarations
- [ ] Zero transitions on layout properties (`width`, `height`, `top`, `left`, `margin`, `padding`)
- [ ] `prefers-reduced-motion` implemented

## Verification

```bash
# 1. Flag remaining untransitioned interactive states
rg --pcre2 ':(hover|active|focus)' --glob '*.{css,scss,tsx}' -l | \
  xargs -I{} sh -c 'grep -L "transition" "{}"'

# 2. Flag transition: all
rg 'transition:\s*all' --glob '*.{css,scss,tsx}'

# 3. Flag layout property transitions
rg --pcre2 'transition:.*\b(width|height|top|left|right|bottom|margin|padding)\b' --glob '*.{css,scss}'

# 4. Confirm reduced-motion query
rg 'prefers-reduced-motion' --glob '*.{css,scss}'
```
