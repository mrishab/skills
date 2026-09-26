---
name: react-declarative-purity
description: Audits and eliminates all direct DOM manipulation anti-patterns from React codebases, enforcing React's declarative paradigm.
version: 1.0.0
author: mrishab
tags: [react, typescript, frontend, dom, architecture]
---

# React Declarative Purity

Enforces React's declarative state-driven UI model (`UI = f(state)`). Prohibits direct DOM manipulation and restricts `useRef` to legitimate non-destructive escape hatches.

## Prohibited DOM APIs

Never use native DOM mutation or query APIs in React components:
1. `document.querySelector`, `document.getElementById`, `document.getElementsBy*`
2. `element.classList.add`, `classList.remove`, `classList.toggle`
3. `document.createElement`, `appendChild`, `removeChild`, `insertBefore`
4. `element.innerHTML`, `element.outerHTML`
5. `element.style.<prop> = ...`

### Permitted `useRef` Escape Hatches
- Focus & text selection: `inputRef.current?.focus()`
- Scroll position: `elementRef.current?.scrollIntoView()`
- Geometry measurements: `getBoundingClientRect()`, `ResizeObserver`
- Media playback: `videoRef.current?.play()`
- Unmanaged third-party leaf containers (D3, Leaflet) where React never renders children
- Imperative animation engines (GSAP, Web Animations API)

## Discovery Commands

```bash
# Global DOM queries & mutations
rg 'document\.(querySelector|getElementById|getElementsBy|createElement|head|body)' --glob '*.{tsx,jsx,ts}'

# Class list manipulation
rg 'classList\.(add|remove|toggle|contains)' --glob '*.{tsx,jsx,ts}'

# Imperative DOM tree alterations
rg '\.(appendChild|removeChild|insertBefore|replaceChild|innerHTML|outerHTML)' --glob '*.{tsx,jsx,ts}'

# Imperative style mutations
rg '\.style\.[a-zA-Z]+ *=' --glob '*.{tsx,jsx,ts}'
```

## Anti-Patterns & Replacements

### 1. Element Selection & Value Access
```tsx
// ❌ BAD
const val = document.getElementById('search-input').value;

// ✅ GOOD: Controlled input
const [val, setVal] = useState('');
<input value={val} onChange={(e) => setVal(e.target.value)} />
```

### 2. Class List Mutation
```tsx
// ❌ BAD
element.classList.toggle('active');

// ✅ GOOD: State-driven className
const [isActive, setIsActive] = useState(false);
<button className={clsx('btn', isActive && 'active')} onClick={() => setIsActive(!isActive)}>
```

### 3. Modals & Appending to Body
```tsx
// ❌ BAD
const modal = document.createElement('div');
document.body.appendChild(modal);

// ✅ GOOD: Portals
import { createPortal } from 'react-dom';
{isOpen && createPortal(<ModalContent onClose={() => setIsOpen(false)} />, document.body)}
```

### 4. Focus Management
```tsx
// ❌ BAD
document.querySelector('input[name="email"]').focus();

// ✅ GOOD: Scoped ref
const inputRef = useRef<HTMLInputElement>(null);
useEffect(() => { inputRef.current?.focus(); }, []);
<input ref={inputRef} name="email" />
```

### 5. Third-Party Libraries (D3, Charts, Maps)
```tsx
// ❌ BAD: D3 mutates inside React-managed elements
function Chart({ data }) {
  const ref = useRef(null);
  useEffect(() => { d3.select(ref.current).selectAll('circle').data(data)...; });
  return <svg ref={ref}><g className="chart" /></svg>;
}

// ✅ GOOD: Isolated leaf node. React renders empty wrapper; D3 owns internals
function Chart({ data }) {
  const containerRef = useRef<HTMLDivElement>(null);
  useEffect(() => {
    if (!containerRef.current) return;
    containerRef.current.innerHTML = '';
    const svg = d3.select(containerRef.current).append('svg');
    // ... render chart
    return () => { if (containerRef.current) containerRef.current.innerHTML = ''; };
  }, [data]);
  return <div ref={containerRef} />;
}
```

### 6. Script Injection
```tsx
// ❌ BAD
const s = document.createElement('script');
s.src = 'https://example.com/lib.js';
document.head.appendChild(s);

// ✅ GOOD (React 19+)
<script src="https://example.com/lib.js" async />
```

## Verification Checklist

- [ ] `rg 'document\.(querySelector|getElementById)' --glob '*.{tsx,jsx,ts}'` clean (except tests/leaf wrappers)
- [ ] `rg '\.classList\.' --glob '*.{tsx,jsx,ts}'` returns zero matches
- [ ] `rg '\.(appendChild|innerHTML)' --glob '*.{tsx,jsx,ts}'` clean (except third-party cleanup)
- [ ] No `useRef` used for text content or styling mutations
