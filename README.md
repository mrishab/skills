# mrishab/skills

[![Validate Skills](https://github.com/mrishab/skills/actions/workflows/validate.yml/badge.svg)](https://github.com/mrishab/skills/actions/workflows/validate.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](./LICENSE)
[![Standard: Open Agent Skills](https://img.shields.io/badge/Standard-Open%20Agent%20Skills-green.svg)](./SKILL_SPEC.md)

Personal AI agent skills by **Rishab Manocha ([@mrishab](https://github.com/mrishab))**, installed across Claude Code, Google Antigravity, OpenCode, Codex, and Cursor.

---

## Quick Start

### 1. Install All Skills
Symlinks personal and vendor skills globally across all detected agent harnesses:

```bash
make install
```

Target specific agents or custom projects:
```bash
./scripts/install.sh --agent claude              # Claude Code only
./scripts/install.sh --agent antigravity         # Antigravity only
./scripts/install.sh --project /path/to/project  # Local project install
./scripts/install.sh --no-vendor                 # Personal skills only
```

### 2. Check Status
```bash
make status
```

### 3. Install via `skills.sh`
```bash
npx skills add mrishab/skills
```

---

## 📚 Included Skills

| Skill | Description | Location |
| :--- | :--- | :--- |
| **[`transition-polish`](./skills/transition-polish/SKILL.md)** | Maximizes transition coverage across interactive elements with physics-grounded durations, safe properties, and accessibility rules. | [skills/transition-polish](./skills/transition-polish/) |
| **[`theme-purity`](./skills/theme-purity/SKILL.md)** | Enforces strict semantic theme architecture, eliminates hardcoded colors, and ensures light/dark parity across UI and widgets. | [skills/theme-purity](./skills/theme-purity/) |
| **[`ux-copy-fitness`](./skills/ux-copy-fitness/SKILL.md)** | Audits and reduces unnecessary text across an entire web application, enforcing concise, scannable, action-oriented UI copy. | [skills/ux-copy-fitness](./skills/ux-copy-fitness/) |
| **[`react-declarative-purity`](./skills/react-declarative-purity/SKILL.md)** | Audits and eliminates direct DOM manipulation anti-patterns, enforcing React's declarative state-driven paradigm. | [skills/react-declarative-purity](./skills/react-declarative-purity/) |
| **[`type-hygiene`](./skills/type-hygiene/SKILL.md)** | Eradicates TypeScript Record anti-patterns, replacing nested Records with domain value objects and nominal branded types. | [skills/type-hygiene](./skills/type-hygiene/) |
| **[`loc-fitness`](./skills/loc-fitness/SKILL.md)** | Enforces a hard 60-line cap on hand-written frontend React components to keep components clean, single-purpose, and maintainable. | [skills/loc-fitness](./skills/loc-fitness/) |
| **[`ai-researcher`](./skills/ai-researcher/SKILL.md)** | Elite AI research paper curation and breakdown. Formulates intuitive, geometrically grounded technical scripts and reviews for advanced AI architectures. | [skills/ai-researcher](./skills/ai-researcher/) |
| **[`build-trishul-api`](./skills/build-trishul-api/SKILL.md)** | Standardized workflow for creating new domain APIs within the Trishul framework (interfaces, entities, DTOs, mappers, services, controllers, migrations). | [skills/build-trishul-api](./skills/build-trishul-api/) |
| **[`fix-mutations`](./skills/fix-mutations/SKILL.md)** | Finds and fixes survived PIT mutation tests across Java/Spring modules in batches of 10 to ensure comprehensive test coverage. | [skills/fix-mutations](./skills/fix-mutations/) |
| **[`trishul-app-sync`](./skills/trishul-app-sync/SKILL.md)** | Synchronizes backend and frontend by building the backend, generating openapi.json, and generating type-safe TypeScript models & Orval hooks. | [skills/trishul-app-sync](./skills/trishul-app-sync/) |

---

## 🎨 Vendor Skills: Emil Kowalski (`emilkowalski/skills`)

Bundled via git submodule (`vendor/emilkowalski-skills`):

| Vendor Skill | Focus |
| :--- | :--- |
| **`emil-design-eng`** | Design engineering principles and UI craft. |
| **`animate`** | Builds animations from scratch with proper easing curves and durations. |
| **`mobile-native`** | Touch ergonomics, tap highlights, dynamic viewport units, and notch safe-areas. |
| **`review-animations`** | Animation audit and quality review against design engineering rules. |
| **`improve-animations`** | Scans UI and produces prioritized animation remediation plans. |
| **`apple-design`** | Apple interface and motion design principles distilled from WWDC. |
| **`find-animation-opportunities`**| Pinpoints areas that benefit from motion. |
| **`animation-vocabulary`** | Precise motion and spring terminology for prompting agents. |
| **`ask-sonner`** | Guide to configuring, styling, and troubleshooting Sonner toasts. |
| **`pick-ui-library`** | Selection framework for production-grade UI component libraries. |
| **`prototype`** | Builds multi-variant UI prototypes with an interactive switcher. |
| **`animate-expo`** / **`write-swift`** | React Native Reanimated and native SwiftUI motion engineering. |

Update vendor skills:
```bash
make update-vendor
```

---

## 🛠️ Adding a New Skill

```bash
make new NAME=my-skill DESC="Diagnoses build failures. Use when build fails."
```

Validate and auto-generate shims:
```bash
make validate    # Lint against open standards
make fix         # Auto-generate wrappers and fix permissions
```

---

## Repository Structure

```text
skills/
├── scripts/
│   ├── install.sh         # Multi-agent installer (symlink/copy)
│   ├── uninstall.sh       # Clean removal from agent directories
│   ├── validate.py        # Validator (schema, links, wrappers)
│   └── new-skill.sh       # Scaffolder for new skills
├── skills/                # Personal skills (SKILL.md + wrappers)
├── vendor/                # Upstream submodules (emilkowalski-skills)
├── templates/             # Canonical starter template
├── SKILL_SPEC.md          # Open Agent Skills Specification
└── Makefile               # CLI shortcuts
```

---

## License

[MIT](./LICENSE) © 2026 Rishab Manocha
