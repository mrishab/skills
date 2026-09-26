---
name: react-declarative-purity
description: Audits and eliminates all direct DOM manipulation anti-patterns from React codebases, enforcing React's declarative paradigm.
version: 1.0.0
author: mrishab
tags: [react, typescript, frontend, dom, architecture]
---

# React Declarative Purity

**WHEN TO USE:**
Activate this skill whenever auditing, refactoring, or reviewing React codebases (TypeScript/JavaScript). It is strictly enforced for any React component or hook creation/modification to ensure adherence to React's declarative UI model.

## 🧠 The Core Principle: UI = f(state)

React owns the DOM. Direct imperative DOM manipulation creates competing sources of truth, breaks Server-Side Rendering (SSR) and React Server Components (RSC), interferes with Concurrent React, and violates component encapsulation.

As per Dan Abramov's Bug-O notation, imperative DOM updates create O(N²) transition paths between N states. React's declarative model guarantees O(1) complexity per state.

**"No Component is a Singleton"**: Using `document.getElementById('sidebar')` assumes only one sidebar will ever exist. This breaks during route transitions, split-pane views, and SSR.

React documentation explicitly calls refs "Escape Hatches": "You should use them sparingly... manually modifying DOM nodes managed by React can lead to inconsistent UI or crashes."

## ⛔ Zero Tolerance / Hard Rules

You must **NEVER** use the following native DOM APIs to mutate or query the DOM inside React code, unless it falls strictly into a legitimate escape hatch category:
1. `document.querySelector`, `document.getElementById`, `document.getElementsBy*`
2. `element.classList.add`, `classList.remove`, `classList.toggle`
3. `document.createElement`, `appendChild`, `removeChild`, `insertBefore`
4. `element.innerHTML`, `element.outerHTML`
5. `element.style.<property> = ...`

### Legitimate Escape Hatches (When `useRef` is acceptable)
- Managing focus or selection (e.g., `inputRef.current?.focus()`).
- Managing scroll position (e.g., `scrollIntoView()`).
- Measuring element geometry (`getBoundingClientRect`, `ResizeObserver`).
- Media playback (`video.play()`, `video.pause()`).
- Integrating non-React third-party libraries (e.g., D3, Leaflet) in isolated leaf containers where React NEVER reconciles the children.
- Imperative animations (e.g., GSAP, Web Animations API).

## 🔄 The Loop (Discovery & Refactor)

Execute this loop to purify a React codebase:

1. **Search for violations** using the following discovery commands.
2. **For each violation**, read the file context.
3. **Refactor** the imperative code to use idiomatic React state, props, refs, or portals.
4. **Verify** using the checklist.

### Discovery Commands

Run these exact `rg` commands to find anti-patterns across the codebase:

```bash
# Find global DOM queries and document modifications
rg 'document\.(querySelector|getElementById|getElementsBy|createElement|head|body)' --glob '*.{tsx,jsx,ts}'

# Find imperative class list mutations
rg 'classList\.(add|remove|toggle|contains)' --glob '*.{tsx,jsx,ts}'

# Find direct DOM structure mutations
rg '\.(appendChild|removeChild|insertBefore|replaceChild|innerHTML|outerHTML)' --glob '*.{tsx,jsx,ts}'

# Find imperative style mutations
rg '\.style\.[a-zA-Z]+ *=' --glob '*.{tsx,jsx,ts}'
```

## ❌ Anti-Patterns vs ✅ Idiomatic React Replacements

### 1. Global DOM Queries
**Anti-Pattern:** Using global selectors for state or focus management.
```tsx
// ❌ BAD: Violates component isolation, breaks if multiple instances exist.
function Modal() {
  const openModal = () => {
    document.getElementById('my-modal').style.display = 'block';
  }
}
```

**Replacement:** Use state and conditional rendering.
```tsx
// ✅ GOOD: State-driven rendering
function Modal() {
  const [isOpen, setIsOpen] = useState(false);
  return (
    <>
      <button onClick={() => setIsOpen(true)}>Open</button>
      {isOpen && <div className="modal-dialog">...</div>}
    </>
  );
}
```

### 2. Imperative Class List Mutation
**Anti-Pattern:** Manually toggling classes.
```tsx
// ❌ BAD: Imperative mutation bypasses React reconciliation
function ToggleButton() {
  const toggle = (e) => {
    e.currentTarget.classList.toggle('active');
  }
  return <button onClick={toggle}>Toggle</button>;
}
```

**Replacement:** Use state-driven `className` (often with `clsx` or `cn`).
```tsx
// ✅ GOOD: Derived from state
function ToggleButton() {
  const [isActive, setIsActive] = useState(false);
  return (
    <button 
      className={clsx('btn', isActive && 'active')} 
      onClick={() => setIsActive(!isActive)}
    >
      Toggle
    </button>
  );
}
```

### 3. Portals vs `appendChild`
**Anti-Pattern:** Creating and appending elements manually for overlays.
```tsx
// ❌ BAD: Creating floating DOM nodes manually
function Tooltip({ children }) {
  useEffect(() => {
    const el = document.createElement('div');
    document.body.appendChild(el);
    return () => document.body.removeChild(el);
  }, []);
}
```

**Replacement:** Use `createPortal`.
```tsx
// ✅ GOOD: Declarative portals
import { createPortal } from 'react-dom';

function Tooltip({ children, isOpen }) {
  if (!isOpen) return null;
  return createPortal(
    <div className="tooltip">{children}</div>,
    document.body // or a specific #portal-root
  );
}
```

### 4. Injecting Scripts
**Anti-Pattern:** Appending scripts to the document head manually.
```tsx
// ❌ BAD: Imperative script injection
useEffect(() => {
  const script = document.createElement('script');
  script.src = 'https://example.com/widget.js';
  document.head.appendChild(script);
}, []);
```

**Replacement:** React 19 native `<script>` hoisting, or a robust `useScript` hook.
```tsx
// ✅ GOOD: Declarative script (React 19+)
function Widget() {
  return (
    <>
      <script src="https://example.com/widget.js" async />
      <div id="widget-root" />
    </>
  );
}
```

### 5. Third-Party Lib Integration
**Anti-Pattern:** Letting React manage the children while D3 mutates them.
```tsx
// ❌ BAD: React and D3 fighting over the DOM
function Chart({ data }) {
  const ref = useRef(null);
  useEffect(() => {
    d3.select(ref.current).selectAll('circle').data(data).enter().append('circle');
  }, [data]);
  return <svg ref={ref}><g className="chart-group" /></svg>; // React will try to reconcile this!
}
```

**Replacement:** Use an isolated leaf node.
```tsx
// ✅ GOOD: Isolated leaf container. React renders an empty div, D3 owns the inside.
function Chart({ data }) {
  const ref = useRef<HTMLDivElement>(null);
  useEffect(() => {
    if (!ref.current) return;
    // D3 clears and renders its own DOM tree inside the div
    const svg = d3.select(ref.current).append('svg'); 
    // ... setup chart
    return () => {
      ref.current.innerHTML = ''; // Cleanup on unmount
    };
  }, [data]);
  
  // React NEVER renders children here
  return <div ref={ref} />;
}
```

## ✅ Verification Checklist

Before considering the task complete, ensure all these checks pass with zero problematic outputs:

- [ ] `rg 'document\.(querySelector|getElementById)' --glob '*.{tsx,jsx,ts}'` returns no results (except in tests or strictly isolated third-party wrappers).
- [ ] `rg '\.classList\.' --glob '*.{tsx,jsx,ts}'` returns no results.
- [ ] `rg '\.(appendChild|innerHTML)' --glob '*.{tsx,jsx,ts}'` returns no results outside of specialized cleanup routines for third-party libs.
- [ ] Verify that any remaining `useRef` usages are strictly for reading geometry, focusing, media control, or passing to an opaque third-party library, and NEVER for modifying `className` or text content.
