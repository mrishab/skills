---
name: loc-fitness
description: Enforces a hard 60-line cap on frontend React components (non-auto-generated). Use when frontend/src files grow too large or to refactor a component past the cap. Trigger keywords: line count, LOC, refactor component, split component, 60 lines, top files by lines of code, large file, too many lines, reduce lines.
version: 1.0.0
author: mrishab
tags: [react, refactoring, clean-code, loc]
---

# LOC Fitness: 60-Line React Component Cap

Enforces a hard limit of **maximum 60 lines** per hand-written React component and hook in `web/src` (and `mobile/src`).

## Scope & Exclusions

- **Governed:** Hand-written React components (`.tsx`) and hooks (`use*.ts`).
- **Excluded:** Auto-generated code (`lib/api/model/**`, `lib/api/client.ts`, orval output), tests (`*.test.ts`, `cypress/**`), configs (`vite.config.ts`), and static enum/constant files.

## The Loop

Run until all non-generated `web/src` components and hooks are ≤60 lines:

```bash
cd web
wc -l **/*.ts* | sort -k 1 -r | head -n 12 | tail -n 10
```

For each file over 60 lines:
1. Refactor using the sequence below.
2. Verify: lint, format, line count.
3. Repeat.

## Decomposition Sequence

Apply steps in order until the file is ≤60 lines:

1. **Extract Non-Render Code (Cheapest):**
   - Constants → `constants.ts` beside the component, or shared `lib/`
   - Type definitions / interfaces → `types.ts`
   - Utility functions → `lib/` helper modules

2. **Separate Logic into `use<Component>.ts`:**
   - `<Component>.tsx` owns JSX render only (`const d = use<Component>()`).
   - `hooks/use<Component>.ts` owns state, data queries, and mutations.
   - If `use<Component>.ts` exceeds 60 lines, split into sub-hooks (`use<Feature>Queries`, `use<Feature>Form`, `use<Feature>Mutations`).

3. **Extract Render Sub-Components:**
   - Extract cards, table rows, button groups, or filter bars into dumb sub-components under `components/`.
   - Pass typed hook return data: `data: ReturnType<typeof use<Component>>` plus explicit callbacks.

4. **Extract Edge States:**
   - Move loading skeletons, error states, and empty states into dedicated components (`<FeatureLoading />`, `<FeatureEmpty />`).

## Hard Rules

- **Every extracted piece must itself be ≤60 lines.**
- **Format before measuring:** Always run `prettier --write` before checking line count (Prettier re-expands compressed JSX).
- **Import cycle avoidance:** `types.ts` must never import from `hooks/`. Sub-components import shared types from `types.ts`.

## Verification Commands

Run per refactored file:

```bash
npx eslint <file>                  # Must exit 0
npx prettier --write <file>        # Format
wc -l <file>                       # Must be <= 60 AFTER prettier
```

Full scan:
```bash
find src -name "*.ts" -o -name "*.tsx" | \
  grep -v "lib/api/model" | grep -v "lib/api/client.ts" | grep -v "/dist/" | \
  xargs wc -l | sort -k1 -r | awk '$1 > 60'
```