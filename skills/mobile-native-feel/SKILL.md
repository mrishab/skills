---
name: mobile-native-feel
description: >-
  Use this skill to make web applications feel native and performant on mobile devices and touch screens. It provides solutions for common mobile web issues like tap lag, hover states, layout heights, input zooming, scrolling, and notch area handling.
---

# Mobile Native Feel

This skill provides a set of best practices and quick CSS/HTML fixes to ensure web applications feel native, responsive, and polished when viewed on mobile screens and touch devices.

## Quick Reference Table

| Problem | Solution | Description / CSS Rule |
| :--- | :--- | :--- |
| **Hover state stuck after tap** | Wrap in `@media (hover: hover) and (pointer: fine)` | Keeps hover animations active only on devices that support hover (e.g. mouse pointers), preventing sticky hover states on touch taps. |
| **Gray/blue flash on tap** | Kill `-webkit-tap-highlight-color` | `* { -webkit-tap-highlight-color: transparent; }` |
| **Layout has wrong height** | `100dvh` (app) or `100svh` (hero) | Dynamic viewport height adjusts for mobile browser chrome; small viewport height keeps a reliable minimum size. |
| **Page zooms into input** | Input's font size should be 16px at the minimum | iOS Safari auto-zooms if inputs are `< 16px`. Ensure `font-size: 16px` (or `font-size: 1rem` equivalent) is used for text inputs. |
| **Tap feels laggy** | Feedback on pointer-down + `touch-action: manipulation` | Eliminates the 300ms tap delay and provides instant visual states. |
| **Pull-to-refresh hijacks scroll** | `overscroll-behavior: none` on `html, body` | Prevents pull-to-refresh or bounce gestures from interrupting page scrolling. |
| **Content stops at the notch** | `viewport-fit=cover` + `env(safe-area-inset-*)` | `<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">` combined with safe area padding. |
| **Long-press selects button text** | Add `user-select: none` | Prevents the default text selection highlighting when long-pressing interactive elements. |
| **Carousel scrolls vertically** | `touch-action: pan-y` on the gesture surface | Restricts touch actions to horizontal swipes, avoiding accidental vertical scrolling. |
| **Status bar color doesn't match** | `theme-color` per color scheme | `<meta name="theme-color" content="#ffffff" media="(prefers-color-scheme: light)">` |
| **Right in chrome, wrong on phone** | Test on real hardware! | Always perform QA on actual touch devices to verify interactions. |

## Implementation Details

### 1. Stuck Hover States
To prevent hover states from remaining active after a user taps on a touch screen:
```css
@media (hover: hover) and (pointer: fine) {
  .btn:hover {
    background-color: var(--btn-hover-bg);
  }
}
```

### 2. Tap Highlight & Tap Delay
Remove the default tap highlight color on mobile WebKit browsers and ensure fast touch response:
```css
button, a, [role="button"] {
  -webkit-tap-highlight-color: transparent;
  touch-action: manipulation;
}
```

### 3. Handle Viewport Heights
Avoid `100vh` on mobile, which doesn't account for mobile browser UI bars. Use `dvh` (dynamic viewport height) or `svh` (small viewport height):
```css
.app-container {
  height: 100dvh;
}
.hero-section {
  height: 100svh;
}
```

### 4. Input Auto-Zoom
iOS Safari automatically zooms in on input elements with a font size less than `16px`. Set a minimum font size to prevent this zoom behavior:
```css
input[type="text"], input[type="email"], textarea, select {
  font-size: 16px;
}
```

### 5. Prevent Text Selection on Buttons
Avoid text selection overlays during taps or long presses on buttons:
```css
button, .btn {
  user-select: none;
  -webkit-user-select: none;
}
```

### 6. Notch and Safe Areas
Ensure that full-screen layouts expand behind the notch, using safe area variables to pad the actual content:
```html
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
```
```css
body {
  padding-top: env(safe-area-inset-top);
  padding-bottom: env(safe-area-inset-bottom);
  padding-left: env(safe-area-inset-left);
  padding-right: env(safe-area-inset-right);
}
```
