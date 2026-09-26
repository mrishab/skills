# Open Agent Skills Specification

Authoring standards for skills in this repository. Skills follow the vendor-agnostic **Open Agent Skills Standard** (`SKILL.md`), inter-operating across Claude Code, Google Antigravity, OpenCode, Codex, Cursor, and modern agent harnesses.

---

## 1. Directory Structure

Each skill lives under `skills/<skill-name>/`:

```text
skills/<skill-name>/
├── SKILL.md            # [REQUIRED] Canonical instructions with YAML frontmatter
├── AGENTS.md           # [AUTO-GENERATED] Fallback pointer for markdown-only harnesses
├── agents/             # [AUTO-GENERATED] Proprietary harness metadata
│   └── openai.yaml     # OpenAI Codex display strings
├── scripts/            # [OPTIONAL] Executable utilities (chmod +x)
├── references/         # [OPTIONAL] Deep documentation, specs, and reference tables
├── examples/           # [OPTIONAL] Code samples and patterns
└── resources/          # [OPTIONAL] Static assets, schemas, templates
```

---

## 2. `SKILL.md` Specification

`SKILL.md` is the single source of truth for the skill.

### Frontmatter Schema

Every `SKILL.md` must start with YAML frontmatter:

```yaml
---
name: my-skill-name
description: >-
  Action-oriented summary of what the skill does and trigger criteria.
version: 1.0.0
author: Rishab Manocha
tags: [tag1, tag2]
---
```

#### Fields
- **`name`** *(required)*: Lowercase kebab-case (`^[a-z0-9]+(-[a-z0-9]+)*$`). Must match the directory name.
- **`description`** *(required)*: Routing text loaded into agent index. State clearly **what** the skill does and **when** to activate. Third-person.
- **`version`** *(optional)*: Semantic version (`X.Y.Z`).
- **`tags`** *(optional)*: List of domain tags.

### Content Sections
1. **Title (`# Skill Name`)**: Clear heading.
2. **Trigger Criteria**: When to activate and when to reject.
3. **Workflow / Step-by-Step Instructions**: Concrete, actionable steps with exact commands.
4. **Hard Rules & Anti-Patterns**: Explicit constraints and code examples (❌ Bad vs ✅ Good).
5. **Verification**: Concrete commands to confirm completion before finishing.

---

## 3. Helper Scripts (`scripts/`)

- Must be idempotent and executable (`chmod +x`).
- Valid shebang required (`#!/usr/bin/env bash` with `set -euo pipefail`, or `#!/usr/bin/env python3`).

---

## 4. Minimal Wrappers (`AGENTS.md` & `agents/openai.yaml`)

- Kept in sync automatically via `./scripts/validate.py --fix` or `make fix`.
- `AGENTS.md` points markdown-only harnesses to `SKILL.md`.
- `agents/openai.yaml` specifies Codex UI display strings.
