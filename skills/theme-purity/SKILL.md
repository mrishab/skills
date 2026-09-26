---
name: theme-purity
description: Audits and fixes hardcoded colors to ensure seamless light/dark theme support and eliminates theme inconsistencies, including in third-party widgets. Activate when working on theme support, dark mode issues, or removing hardcoded styles.
version: 1.0.0
author: mrishab
tags:
  - ui
  - styling
  - css
  - dark-mode
  - design-system
---

# Theme Purity Skill

This skill enforces a strict, semantic theme architecture to ensure applications can support multiple themes (like light/dark modes) flawlessly. It explicitly prohibits hardcoded color values and enforces the use of semantic design tokens across application code, CSS, and third-party widgets.

## 🎯 Trigger Criteria

Activate this skill when:
- Adding or fixing light/dark mode support.
- Extracting a design system or standardizing UI components.
- Fixing UI contrast issues, "invisible text", or unstyled scrollbars in dark mode.
- Integrating or fixing third-party widgets (editors, charts, maps) that do not match the current app theme.
- The user requests to "fix hardcoded colors" or "audit styles".

## 🛑 Hard Rules & Zero Tolerance

1. **NO HARDCODED COLORS:** Hardcoded colors (hex, rgb, hsl, literal named colors like `white` or `black`) are strictly prohibited in application code. Every color must resolve through a CSS custom property (e.g., `var(--color-primary)`).
2. **USE SEMANTIC NAMING:** Variables must describe *purpose*, not *appearance*. 
   - ❌ `--color-red-500` or `--color-blue`
   - ✅ `--color-danger` or `--color-brand`
3. **MANDATORY `color-scheme`:** The CSS `color-scheme` property must be set on the `:root` element. Without it, native UI elements (scrollbars, form inputs, checkboxes, select dropdowns) will remain light in dark mode.
4. **NO DIRECT PRIMITIVE ACCESS:** Application code (JSX, HTML, CSS components) must NEVER reference Tier 1 primitive tokens (e.g., `--gray-900`) directly. They must use Tier 2 Semantic or Tier 3 Component tokens.
5. **DARK MODE IS NOT INVERSION:** Do not use CSS filters like `filter: invert(1) hue-rotate(180deg)`. Dark themes require:
   - Elevation via lightness tinting, not drop shadows.
   - Off-white text (e.g., `#ededed`, not `#ffffff`) to avoid irradiation/halation.
   - Desaturated accent colors for better contrast and reduced eye strain.

## 🏗️ 3-Tier Token Architecture

1. **Primitives (Tier 1):** Raw values (e.g., `--slate-900: #0f172a`). Only defined in the base theme.
2. **Semantics (Tier 2):** Purpose-driven tokens mapped to primitives (e.g., `--surface-canvas: var(--slate-900)`).
3. **Components (Tier 3):** Component-specific tokens mapped to semantics (e.g., `--button-bg: var(--color-primary)`).

*Application code should only ever touch Tier 2 and Tier 3.*

The standard baseline follows the `shadcn/ui` pattern using semantic CSS variables with separate `:root` and `.dark` blocks:
```css
@layer base {
  :root {
    --background: 0 0% 100%;
    --foreground: 222.2 84% 4.9%;
    --card: 0 0% 100%;
    --primary: 222.2 47.4% 11.2%;
    --destructive: 0 84.2% 60.2%;
    --border: 214.3 31.8% 91.4%;
  }

  .dark {
    --background: 222.2 84% 4.9%;
    --foreground: 210 40% 98%;
    --card: 222.2 84% 4.9%;
    --primary: 210 40% 98%;
    --destructive: 0 62.8% 30.6%;
    --border: 217.2 32.6% 17.5%;
  }
}
```

## 🧩 Third-Party Widget Theming

Third-party widgets often bypass standard CSS inheritance. Handle them specific to their APIs:

| Widget Type | Theming Strategy |
| :--- | :--- |
| **CodeMirror** | Accepts CSS variables directly via `EditorView.theme({ "&": { backgroundColor: "var(--background)" } })` |
| **Monaco Editor** | Requires imperative registration via `monaco.editor.setTheme()`. Map theme tokens explicitly in the setup script. |
| **SVG Charts (Recharts)** | Accept CSS variables directly in `stroke` and `fill` attributes. |
| **Canvas Charts (Chart.js)** | Canvas cannot read CSS directly. Use a `getComputedStyle()` bridge to extract resolved CSS variables and pass them to the chart configuration on theme change. |
| **Maps (Mapbox)** | Require `map.setStyle()` for vector tiles, plus CSS variables for custom DOM overlays. |

## 🔄 The Loop

To enforce theme purity, run this workflow:

1. **Scan for Hardcoded Colors:** Use the discovery commands in the Audit section.
2. **Extract to Theme:** For each hardcoded value, identify its semantic purpose and map it to an existing or new CSS variable in the theme file.
3. **Replace with Semantic Token:** Update the application code to use the semantic CSS variable or corresponding utility class.
4. **Verify:** Run the audit commands again to ensure no violations remain.
5. **Visual Test:** Toggle between light and dark modes to ensure contrast and consistency.

## 🔍 Discovery & Audit Commands

Use these exact shell commands to find theme violations in the codebase:

```bash
# 1. Detect hardcoded hex colors
rg -n "(?i)#[0-9a-f]{3,8}\b" --glob "!*.{css,scss}"

# 2. Detect rgb/rgba/hsl/hsla functions
rg -n "\b(rgb|hsl)a?\([^)]+\)" --glob "!*.{css,scss}"

# 3. Detect Tailwind arbitrary color escapes
rg -n "(bg|text|border|fill|stroke)-\[#" 

# 4. Detect hardcoded Tailwind spectral colors (Tier 1 primitive usage)
rg -n "(bg|text|border|fill|stroke)-(slate|gray|zinc|neutral|stone|red|orange|amber|yellow|lime|green|emerald|teal|cyan|sky|blue|indigo|violet|purple|fuchsia|pink|rose)-[0-9]{2,3}"

# 5. Detect inline style color bindings in JSX/TSX
rg -n "style=\{\{\s*[^}]*(color|background|borderColor)\s*:\s*['\"].*?['\"]" 
```

## ❌ Anti-Patterns vs ✅ Correct Patterns

| Scenario | ❌ Anti-Pattern | ✅ Correct Pattern |
| :--- | :--- | :--- |
| **Inline Styles** | `style={{ color: '#ff0000' }}` | `className="text-destructive"` (Use semantic classes; reserve `style={{}}` only for dynamic runtime coordinates/offsets) |
| **Tailwind Spectral** | `className="bg-gray-900 text-white"` | `className="bg-background text-foreground"` |
| **Tailwind Arbitrary**| `className="bg-[#1e293b]"` | `className="bg-surface-canvas"` |
| **CSS-in-JS** | `styled.div\`color: black;\`` | `styled.div\`color: var(--text-primary);\`` |
| **Dark Mode Hack** | `filter: invert(1) hue-rotate(180deg)` | Proper `color-scheme` and semantic tokens |

## ✅ Verification Checklist

Before concluding your task, ensure the following pass:

1. [ ] The app specifies `color-scheme: light dark;` on `:root`.
2. [ ] `rg -n "(?i)#[0-9a-f]{3,8}\b" --glob "!*.{css,scss}"` returns no results in application code.
3. [ ] `rg -n "(bg|text|border|fill|stroke)-\[#"` returns no results.
4. [ ] Third-party widgets (charts, editors) correctly respond to dynamic theme toggles without page reloads.
5. [ ] Native scrollbars and form controls adapt to dark mode correctly.
