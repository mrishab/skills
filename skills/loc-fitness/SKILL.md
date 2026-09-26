---
name: loc-fitness
description: Enforces a hard 60-line cap on frontend React components (non-auto-generated). Use when frontend/src files grow too large or to refactor a component past the cap. Trigger keywords: line count, LOC, refactor component, split component, 60 lines, top files by lines of code, large file, too many lines, reduce lines.
---

# LOC Fitness Skill

Enforce a hard cap of **max 60 lines per component** for hand-written source in
`web/src` (and `mobile/src`). Auto-generated code (`lib/api/model/**`, `lib/api/client.ts`,
orval output) is excluded — never hand-edit generated files.

## The loop

Set up a **goal** to track this work, then run a loop until every
non-auto-generated `web/src` file is at or below 60 lines.

Work in the `web/src` directory (NOT the repo root) so `node_modules` and
unrelated files never appear in the results:

```
wc -l **/*.ts* | sort -k 1 -r | head -n 12 | tail -n 10
```

The 10 largest files are the currently-over-cap candidates. For each file that
is **non-auto-generated** and over 60 lines:

1. Read it fully.
2. Refactor it down to at or below 60 lines using the patterns below.
3. Re-run the loop.
4. Repeat until every non-auto-generated file is within the cap, then close the goal.

## Refactor patterns (prefer in this order)

### 1. One file == one component

A single `.tsx`/`.ts` file must own exactly **one** component. Any loose class,
standalone function, or constant that is not that component's own render body
belongs in its own dedicated file:

- shared constants → `lib/` constants file (e.g. `lib/keys.ts`) or a
  `constants.ts` next to the component
- type definitions / shared DTO interfaces → `types.ts` (or into an existing
  model module)
- free-standing functions → a named util module under `lib/`

### 2. Split a complex / big render into reusable sub-components
A component whose `return (...)` render is large should delegate pieces to
existing reusable sub-components. Prefer to **generalize an existing
subcomponent** that already fits the need, then reuse it — do not copy-paste.

- extract repeated markup (a row, a card, a row header, a label+input, a stats
  block) into a sub-component file under `components/`
- pass plain data + callback props; keep subcomponents render-only and dumb

### 3. Separate rendering from functional logic
For a single component, split out the non-render logic and data into a
component-specific hook:

- `<ComponentName>.tsx` — owns the render (JSX) only, pulls data via the hook
- `hooks/use<ComponentName>.ts` — functional component defining state, calling
  other hooks, and owning data / api / mutation logic

The hook file must ALSO satisfy the 60-line cap. If a hook exceeds it, split it
one level further: extract sub-hooks (e.g. `useTenantForm`, `useTenantList`,
`useTenantMutations`) and compose them inside `use<ComponentName>`.

## Decomposition playbook (apply this order per over-cap file)

This is the battle-tested sequence for dividing up a large module. Apply the
steps **in this order** — each is cheaper than the next, and doing the cheap
ones first often gets a file under the cap without heavier restructuring. After
every step, re-run `wc -l`; stop as soon as the file is ≤60.

**Step 0 — Measure & baseline.** Find over-cap files (see The loop). Record the
over-cap count up front; it is your completion gate.

**Step 1 — Shed "loose" non-render code (cheapest).** Before touching JSX, move
anything that is not the component's own render body into its own file:
- constants → `constants.ts` beside the component, or a `lib/keys.ts`-style file
- type definitions / interfaces → `types.ts`
- free-standing functions → a named util module (e.g. `formatX.ts`,
  `customerContactUtils.ts`)
This removes "noise" lines with zero render impact and is often enough alone.

**Step 2 — Slim the import block + props interface.** A props interface plus a
10-line import block can consume 15-25 of the 60 lines. Reclaim it:
- export the props/types from a shared `types.ts`
- type the sub-component's data prop as
  `data: ReturnType<typeof use<Component>>` (exported from `types.ts`) so the
  sub-component receives the whole typed hook result without re-importing the
  hook or redeclaring its shape.

**Step 3 — Separate rendering from logic into `use<Component>`.** `<Component>.tsx`
owns render only and does `const d = use<Component>()`; `hooks/use<Component>.ts`
owns state, data, and mutations. Pass `d` (or slices of it) plus callbacks to
dumb sub-components — keep sub-components render-only.

**Step 4 — If the hook is still over 60, split it into composed sub-hooks.**
`use<Component>` becomes a thin composition of `use<Feature>Form`,
`use<Feature>List`, `use<Feature>Mutations`, etc. Each sub-hook must also be ≤60.

**Step 5 — If the render is still over 60, extract render pieces into dumb
sub-components.** A row, a card, a tab bar, an action-button group, a status
badge, a meta block — each into its own file. Pass plain `data` + callbacks.
Prefer generalizing an existing subcomponent over copy-paste.

**Step 6 — Split guard / edge-state renders into dedicated files.** Loading,
not-found, and empty states become their own components so the page reduces to
`guard ? <XxxLoading/> : <compose subcomponents/>`.

**Step 7 — Hoist genuinely-shared helpers the decomposition surfaced.**
After splitting several files, promote helpers used across components (formatters,
option builders, constants) to `lib/` / `hooks/` and reuse them.

### Hard-won constraints (do not skip)

- **Every extracted piece must itself be ≤60 lines.** Splitting a 300-line file
  into two 150-line files is NOT success — re-run the loop on the new files too.
- **The Prettier re-expansion trap.** Compressing JSX onto single lines does NOT
  survive `prettier --check` — Prettier re-expands multi-attribute JSX elements
  onto multiple lines. Extract a sub-component instead of trying to blindly
  compact. Always run `prettier --write` AFTER reaching the target count, then
  re-confirm the file is still ≤60 (Prettier may expand it further).
- **Decompose in dependency order** (foundations → dependents) so the tree stays
  compiling at every step: util/constants → types → hooks → sub-components → page.
- **Do it server-side for identical pieces**: when a sub-piece (a row, a badge,
  a selector item) is reused across many files, extract it once into a shared
  `components/` module and import everywhere — don't duplicate per page.

## Verification recipes

### Scan for over-cap files (exclude generated/config/test)
```bash
cd web
find . -name "*.ts" -o -name "*.tsx" | \
  grep -v node_modules | grep -v "lib/api/model" | grep -v "lib/api/client.ts" \
  | grep -v "/dist/" | xargs wc -l | sort -k1 -r | awk '$1 > 60'
```

### Per-file loop gate
After refactoring any file, run all three (a file is only "done" when all pass):
```bash
npx eslint <file>                  # must exit 0
npx prettier --write <file>        # format, then RE-CHECK line count
wc -l <file>                       # must be <= 60 AFTER prettier
```

### Scope of the cap (what must hit 60 vs what is exempt)
The 60-line cap applies to **React components and hooks**. These are **out of
scope** and may legitimately stay over 60:
- build/config files: `vite.config.ts`, `orval.config.ts`
- test files: `cypress/**`, `*.test.ts`, `*.spec.ts`
- utility / helper modules with no render (e.g. `lib/errorHandler.ts`,
  `ops/dashboardStats.ts`, `lib/ripple.ts`, `hooks/translationData.ts`)
- **constants/enum files** that export static mappings (e.g.
  `components/order/OrderRowMeta.ts` — status → icon/badge mappings). If a file
  exports no component and no hook, it is not governed by the cap.

## Data-passing convention (canonical)

- The page does `const d = use<Component>()` — the hook result is conventionally
  named `d`.
- Dumb sub-components receive `data: ReturnType<typeof use<Component>>` plus
  explicit callbacks — **not** a hand-rebuilt, partially-overlapping props
  interface. Export the `ReturnType` type from a shared `types.ts` so the
  sub-component imports the type without re-importing the hook or redeclaring
  the hook's shape.

## Hook fan-out vocabulary

When a page-level hook exceeds 60 lines, split it into role-specific sub-hooks
(generalize consistently so every page follows the same pattern):
- `use<X>Queries` — reads / data fetching, with `enabled:` guards on id-dependent calls
- `use<X>Mutations` / `use<X>Action` — writes / API mutations
- `use<X>Form` / `use<X>FormState` — local form state and field updates

`use<X>` becomes a thin composition of these. Each sub-hook must itself be ≤60.

## Decomposition is a cascade (plan for ≥2 levels)

One extraction rarely passes. Expect fan-out to recurse:
- page → sub-components **and** page-hook → sub-hooks → (if needed) a second level of sub-hooks
- Example: `ImageCaptureField.tsx` (318 lines) became 1 main component + 1 composed
  hook (`useImageCaptureField`) + 4 sub-hooks + 4 sub-components + 1 lib helper.
Plan for multiple extractions per file instead of assuming one split is enough.

## Hoist pure non-UI helpers first

Value formatters, option/status builders, and pagination / infinite-query hooks
are pure logic with no DOM — prime first-extraction candidates because they drop
lines with zero JSX risk. Seen in this refactor: `useOrderPagination`,
`useOrderStatusOptions`, `formatPrescriptionDisplay`, `orderDisplayUtils`.

## Import-cycle trap

Splitting a big file can introduce circular imports between the new hook and its
sub-components (component imports the hook's `ReturnType` while the hook imports
the component's `types.ts`). Rule: `types.ts` must **not** import from `hooks/`;
sub-components should import the shared type from `types.ts`, never reverse-import
the hook.

## Guard rails

- Do NOT refactor `lib/api/**` (orval-generated) — it is regenerated from the
  backend OpenAPI spec.
- Do not change behavior; this is a structural refactor only.
- Keep imports tidy; prefer the existing `@/` alias for absolute imports.
- After the loop completes, run `npm run check` (lint + prettier) and the frontend
  build to confirm nothing broke before finishing.