# Open Agent Skills Specification

This document details the architectural specification and authoring standards for skills in this repository. All skills are developed against the vendor-agnostic **Open Agent Skills Standard** (`SKILL.md`), ensuring full interoperability across Anthropic Claude, Google Antigravity, OpenCode, OpenAI Codex, Cursor, and any modern agent harness.

---

## 1. Directory Structure

Each skill lives in its own dedicated directory under `skills/<skill-name>/`:

```text
skills/<skill-name>/
├── SKILL.md            # [REQUIRED] Canonical open-standard specification with YAML frontmatter
├── AGENTS.md           # [AUTO-GENERATED/MINIMAL] Fallback wrapper for markdown-only harnesses
├── agents/             # [AUTO-GENERATED/MINIMAL] Metadata wrappers for proprietary harnesses
│   └── openai.yaml     # OpenAI Codex display strings
├── scripts/            # [OPTIONAL] Deterministic executable utilities and scripts
├── references/         # [OPTIONAL] Bulky documentation, API tables, and progressive disclosure
├── examples/           # [OPTIONAL] Reference implementations and before/after samples
└── resources/          # [OPTIONAL] Static assets, templates, and boilerplates
```

---

## 2. The `SKILL.md` File

`SKILL.md` is the single source of truth for every skill.

### 2.1 Frontmatter Schema

Every `SKILL.md` MUST begin with a YAML frontmatter block enclosed by `---`:

```yaml
---
name: my-skill-name
description: >-
  Third-person concise explanation of what the skill does and unambiguous trigger conditions.
  Example: "Diagnoses and remediates Next.js App Router performance and hydration issues. Use when analyzing Next.js rendering bottlenecks or build errors."
version: 1.0.0
author: Rishab Manocha
tags: [react, nextjs, performance]
---
```

#### Field Specifications:
- **`name`** *(string, required)*:
  - Must be lowercase kebab-case (`^[a-z0-9]+(-[a-z0-9]+)*$`).
  - Must exactly match the directory name (`skills/<name>`).
- **`description`** *(string, required)*:
  - The routing brain for AI agents. When agents index available skills, they only load names and descriptions into context (progressive disclosure).
  - Must clearly declare **what** the skill accomplishes and **when/triggers** for activation.
  - Written in third person.
- **`version`** *(string, recommended)*:
  - Semantic version (`X.Y.Z`).

### 2.2 Body Sections

1. **Title (`# Skill Title`)**: Human-readable name.
2. **Context & Overview**: Brief background on why the skill exists.
3. **When to Activate (Trigger Criteria)**:
   - Positive triggers: Specific commands, errors, file paths, or questions.
   - Negative triggers (Auto-Rejects): Clear exclusions to avoid hallucinations or unnecessary invocation.
4. **Step-by-Step Workflow**:
   - Imperative, numbered procedures.
   - Prefer deterministic scripts in `scripts/` over asking LLMs to re-derive boilerplate commands.
5. **Verification & Quality Gate**:
   - Clear criteria for the agent to self-check that its actions succeeded before declaring the task finished.

---

## 3. Progressive Disclosure Design

To avoid token bloat and context degradation:
- **Keep `SKILL.md` lean**: Focus on workflow orchestration, rules, and decision trees.
- **Offload reference material to `references/`**: Place API schemas, lengthy specifications, or cheatsheets in markdown files inside `references/` and link to them using relative markdown links (e.g. `[Schema Reference](./references/schema.md)`).
- **Agents only read referenced files when needed**.

---

## 4. Helper Scripts (`scripts/`)

- Scripts should be idempotent, deterministic, and self-contained.
- Always include a valid shebang:
  - Bash: `#!/usr/bin/env bash` with `set -euo pipefail`.
  - Python: `#!/usr/bin/env python3`.
- Must have executable permissions (`chmod +x`).

---

## 5. Minimal Wrappers (`AGENTS.md` and `agents/openai.yaml`)

To maintain maximum compatibility without fracturing the codebase:
- Proprietary harnesses are served by minimal pointer shims.
- Shims never duplicate workflows. They point directly back to `SKILL.md`.
- These shims are automatically generated and kept in sync by `scripts/validate.py --fix` or `make fix`.
