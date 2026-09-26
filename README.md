# mrishab/skills

[![Validate Skills](https://github.com/mrishab/skills/actions/workflows/validate.yml/badge.svg)](https://github.com/mrishab/skills/actions/workflows/validate.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](./LICENSE)
[![Standard: Open Agent Skills](https://img.shields.io/badge/Standard-Open%20Agent%20Skills-green.svg)](./SKILL_SPEC.md)
[![skills.sh](https://img.shields.io/badge/skills.sh-mrishab%2Fskills-purple.svg)](https://skills.sh)

Curated, high-impact personal AI agent skills developed by **Rishab Manocha ([@mrishab](https://github.com/mrishab))**. 

Maintained centrally in this repository and installed universally across all agent harnesses—allowing any coding agent (Claude Code, Google Antigravity, OpenCode, Codex, Cursor, etc.) to use these skills across all repositories without per-repo duplication.

---

## 🎯 Philosophy

1. **Central Single Source of Truth (SSOT):** You develop, refine, and version skills in this repository once.
2. **Open Standards First:** Skills follow the vendor-agnostic [Open Agent Skills Specification](./SKILL_SPEC.md) (`SKILL.md` with YAML frontmatter).
3. **Minimal Wrappers:** Proprietary agent configurations are minimized to lightweight shims (`AGENTS.md`, `agents/openai.yaml`) that point directly back to the open standard files.
4. **Instant Updates via Symlinks:** By default, installation creates managed symlinks from agent discovery directories to this repo. Changes made here take effect across all your agents immediately without reinstalling.
5. **Universal Compatibility:** Works seamlessly with:
   - 🤖 **Anthropic Claude Code** (`~/.claude/skills/`)
   - 🔮 **Google Antigravity** (`~/.gemini/config/skills/`, `.agents/skills/`)
   - ⚡ **OpenCode** (`~/.config/opencode/skills/`)
   - 🧠 **OpenAI Codex** (`~/.codex/skills/`)
   - 💻 **Cursor & IDE Agents** (`~/.cursor/skills/`)
   - 📦 **skills.sh package manager** (`npx skills add mrishab/skills`)

---

## 🚀 Quick Start

### 1. Install Skills to All Agents

Run the installer to link all skills globally across all detected agent harnesses on your machine:

```bash
make install
```

Or run the installer directly with custom options:

```bash
# Install to all detected agents
./scripts/install.sh --agent all

# Install only to a specific agent
./scripts/install.sh --agent claude
./scripts/install.sh --agent antigravity
./scripts/install.sh --agent opencode
./scripts/install.sh --agent codex
```

### 2. Inspect Installation Status

View which skills are active and linked to which agent harnesses:

```bash
make status
```

### 3. Install to a Specific Project Repository

If you want to bundle skills locally inside a specific project rather than globally:

```bash
./scripts/install.sh --project /path/to/your/project
```

### 4. Install via `skills.sh`

```bash
npx skills add mrishab/skills
```

---

## 📚 Included Skills

| Skill | Description | Location |
| :--- | :--- | :--- |
| **[`mobile-native-feel`](./skills/mobile-native-feel/SKILL.md)** | CSS/HTML architectural fixes and techniques to make web apps feel native and performant on mobile touchscreens (tap lag, hover states, viewport heights, input zoom, safe areas). | [skills/mobile-native-feel](./skills/mobile-native-feel/) |
| **[`ai-researcher`](./skills/ai-researcher/SKILL.md)** | Elite AI research paper curation and breakdown. Formulates intuitive, geometrically grounded technical scripts and reviews for advanced AI architectures. | [skills/ai-researcher](./skills/ai-researcher/) |
| **[`build-trishul-api`](./skills/build-trishul-api/SKILL.md)** | Standardized workflow for creating new domain APIs within the Trishul framework (interfaces, entities, DTOs, mappers, services, controllers, migrations). | [skills/build-trishul-api](./skills/build-trishul-api/) |
| **[`loc-fitness`](./skills/loc-fitness/SKILL.md)** | Enforces a hard 60-line cap on hand-written frontend React components to keep components clean, single-purpose, and maintainable. | [skills/loc-fitness](./skills/loc-fitness/) |
| **[`fix-mutations`](./skills/fix-mutations/SKILL.md)** | Finds and fixes survived PIT mutation tests across Java/Spring modules in batches of 10 to ensure comprehensive test coverage. | [skills/fix-mutations](./skills/fix-mutations/) |
| **[`trishul-app-sync`](./skills/trishul-app-sync/SKILL.md)** | Synchronizes backend and frontend by building the backend, generating openapi.json, and generating type-safe TypeScript models & Orval hooks. | [skills/trishul-app-sync](./skills/trishul-app-sync/) |

---

## 🏗️ Repository Architecture

```text
skills/
├── .github/workflows/
│   └── validate.yml       # GitHub Actions CI validation pipeline
├── scripts/
│   ├── install.sh         # Universal installer (symlink/copy, global/project)
│   ├── uninstall.sh       # Clean removal from agent directories
│   ├── validate.py        # Python validator (schema, links, wrappers, scripts)
│   ├── validate.sh        # Shell wrapper for validator
│   └── new-skill.sh       # Scaffolder for new skills
├── templates/
│   └── skill-template/    # Canonical starter template adhering to specification
├── wrappers/              # Documentation & standards for minimal agent shims
├── skills/                # Canonical source of truth for all skills
│   ├── ai-researcher/
│   │   ├── SKILL.md       # Canonical instructions & frontmatter
│   │   ├── AGENTS.md      # Minimal markdown pointer fallback
│   │   └── agents/
│   │       └── openai.yaml# Minimal OpenAI Codex display metadata
│   └── mobile-native-feel/
│       ├── SKILL.md
│       ├── AGENTS.md
│       └── agents/
│           └── openai.yaml
├── Makefile               # Convenient developer shortcuts
├── package.json           # skills.sh & npm package metadata
├── SKILL_SPEC.md          # Open Agent Skills Specification
├── CONTRIBUTING.md        # Authoring guide
└── LICENSE                # MIT License
```

---

## 🛠️ Adding a New Skill

Creating a new skill that is automatically compliant across all agents takes one command:

```bash
make new NAME=my-new-skill DESC="Diagnoses build failures. Use when build fails."
```

This scaffolds:
1. `skills/my-new-skill/SKILL.md` (Open standard with YAML frontmatter)
2. `skills/my-new-skill/AGENTS.md` (Minimal fallback pointer)
3. `skills/my-new-skill/agents/openai.yaml` (Minimal Codex metadata)
4. `scripts/`, `references/`, `resources/`, and `examples/` subdirectories

### Validating Your Skills

Run the test suite to ensure strict adherence to open standards:

```bash
make validate
```

If you ever edit `SKILL.md` and need to update wrappers or fix script permissions automatically, run:

```bash
make fix
```

---

## 🔌 Minimal Wrapper Design

To prevent fragmentation and proprietary lock-in:
- **`SKILL.md`** contains 100% of the operational intelligence, instructions, decision trees, and commands.
- **`AGENTS.md`** is a 4-line pointer for tools or harnesses that only look for Markdown files:
  ```markdown
  # My Skill
  <Description>
  For the canonical instructions, workflows, references, and executable scripts, see [SKILL.md](./SKILL.md).
  ```
- **`agents/openai.yaml`** is a 3-line manifest for OpenAI Codex UI rendering:
  ```yaml
  interface:
    display_name: "My Skill"
    short_description: "Short description..."
  ```

---

## 📄 License

[MIT](./LICENSE) © 2026 Rishab Manocha ([@mrishab](https://github.com/mrishab))
