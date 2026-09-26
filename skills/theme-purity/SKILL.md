---
name: theme-purity
description: Audits and fixes hardcoded colors to ensure seamless light/dark theme support and eliminates theme inconsistencies, including in third-party widgets. Activate when working on theme support, dark mode issues, or removing hardcoded styles.
version: 1.0.0
author: mrishab
tags: [ui, styling, css, dark-mode, design-system]
---

# Theme Purity

Enforces semantic theme architecture for reliable light/dark mode support. Prohibits hardcoded colors and mandates semantic design tokens across application code, CSS, and third-party widgets.

## Hard Rules

1. **Zero Hardcoded Colors:** No raw hex, rgb, hsl, or literal colors (`white`, `black`, `slate-900`) in application code. All colors must resolve via CSS custom properties (e.g. `var(--color-primary)`).
2. **Semantic Naming Only:** Tokens must describe *role*, not hue. Use `--color-danger`, not `--color-red`.
3. **Mandatory `color-scheme`:** Set `color-scheme: light dark;` on `:root` to ensure native controls (scrollbars, form inputs, select dropdowns) render with the correct system theme.
4. **No Direct Primitive Tokens:** Application code consumes Tier 2 Semantic or Tier 3 Component tokens—never Tier 1 Primitives directly.
5. **No Visual Inversion Hacks:** Banned: `filter: invert(1) hue-rotate(180deg)`. Dark themes require elevation via surface lightness tinting, off-white text (`#ededed`), and desaturated accents.

## 3-Tier Token Structure

```text
Tier 1: Primitives   (--slate-900: #0f172a)          -> Theme definitions only
Tier 2: Semantics    (--surface-canvas: var(--slate-900)) -> Consumed by UI components
Tier 3: Components   (--button-bg: var(--color-primary)) -> Component-scoped APIs
```

Baseline (`shadcn/ui` style):
```css
@layer base {
  :root {
    color-scheme: light;
    --background: 0 0% 100%;
    --foreground: 222.2 84% 4.9%;
    --card: 0 0% 100%;
    --primary: 222.2 47.4% 11.2%;
    --destructive: 0 84.2% 60.2%;
    --border: 214.3 31.8% 91.4%;
  }

  .dark {
    color-scheme: dark;
    --background: 222.2 84% 4.9%;
    --foreground: 210 40% 98%;
    --card: 222.2 84% 4.9%;
    --primary: 210 40% 98%;
    --destructive: 0 62.8% 30.6%;
    --border: 217.2 32.6% 17.5%;
  }
}
```

## Third-Party Widgets

| Widget | Strategy |
| :--- | :--- |
| **CodeMirror** | CSS variables via `EditorView.theme({ "&": { backgroundColor: "var(--background)" } })` |
| **Monaco Editor** | Imperative registration via `monaco.editor.setTheme()` triggered by theme change |
| **SVG Charts (Recharts)** | Direct `stroke="var(--color-chart-1)"` and `fill` attributes |
| **Canvas Charts (Chart.js)** | Extract resolved tokens with `getComputedStyle(document.documentElement).getPropertyValue('--token')` on theme update |
| **Maps (Mapbox)** | `map.setStyle()` for tiles; CSS variables for DOM popups and overlays |

## Audit Commands

```bash
# 1. Hardcoded hex colors
rg -n "(?i)#[0-9a-f]{3,8}\b" --glob "!*.{css,scss}"

# 2. Hardcoded rgb/hsl functions
rg -n "\b(rgb|hsl)a?\([^)]+\)" --glob "!*.{css,scss}"

# 3. Tailwind arbitrary color escapes
rg -n "(bg|text|border|fill|stroke)-\[#" 

# 4. Hardcoded Tailwind spectral classes (Tier 1 primitives)
rg -n "(bg|text|border|fill|stroke)-(slate|gray|zinc|neutral|stone|red|orange|amber|yellow|lime|green|emerald|teal|cyan|sky|blue|indigo|violet|purple|fuchsia|pink|rose)-[0-9]{2,3}"

# 5. Inline style color assignments in JSX
rg -n "style=\{\{\s*[^}]*(color|background|borderColor)\s*:\s*['\"].*?['\"]"
```

## Anti-Patterns

| ❌ Anti-Pattern | ✅ Correct Pattern |
| :--- | :--- |
| `style={{ color: '#ff0000' }}` | `className="text-destructive"` |
| `className="bg-gray-900 text-white"` | `className="bg-background text-foreground"` |
| `className="bg-[#1e293b]"` | `className="bg-surface-canvas"` |
| `styled.div\`color: black;\`` | `styled.div\`color: var(--text-primary);\`` |
| `filter: invert(1) hue-rotate(180deg)` | `color-scheme: dark;` + semantic tokens |

## Verification Checklist

- [ ] `color-scheme: light dark;` is set on `:root`
- [ ] No hex/rgb values in application code (`rg -n "(?i)#[0-9a-f]{3,8}\b" --glob "!*.{css,scss}"` clean)
- [ ] No arbitrary color classes (`rg -n "(bg|text|border|fill|stroke)-\[#"` clean)
- [ ] Third-party widgets update without page refresh
- [ ] Scrollbars and inputs render dark in dark mode
