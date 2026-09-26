# Agent Wrappers & Adapters Architecture

This repository strictly adheres to the principle of **Single Source of Truth (SSOT)** using the vendor-agnostic open Agent Skills standard.

## Philosophy

1. **Open Standards First:** Every skill is authored completely within `skills/<skill-name>/SKILL.md` using YAML frontmatter (`name`, `description`) and standard Markdown.
2. **Zero Code Duplication:** Proprietary configurations do NOT re-implement or fork the skill.
3. **Minimal Pointers:** When an agent harness does not natively discover or parse `SKILL.md`:
   - A minimal pointer/shim file is generated or provided.
   - The shim simply points directly to the open standard `SKILL.md` or provides the absolute minimum metadata required by that specific agent.

## Supported Agents & Wrapper Types

| Agent / Harness | Native Support | Adapter / Wrapper Mechanism | Location / Target |
| :--- | :--- | :--- | :--- |
| **Google Antigravity** | Native (`SKILL.md`) | Direct symlink or `skills.json` entry | `~/.gemini/config/skills/<skill>` or `.agents/skills/<skill>` |
| **Anthropic Claude Code** | Native (`SKILL.md`) | Direct symlink | `~/.claude/skills/<skill>` or `.claude/skills/<skill>` |
| **OpenCode** | Native (`SKILL.md`) | Direct symlink | `~/.config/opencode/skills/<skill>` or `.opencode/skills/<skill>` |
| **OpenAI Codex** | Partial | Minimal `agents/openai.yaml` with `interface` metadata + `AGENTS.md` | `~/.codex/skills/<skill>` |
| **Cursor / Windsurf** | Partial | Minimal `AGENTS.md` pointer / `.cursor/rules` pointer | `~/.cursor/skills/<skill>` |
| **Generic LLM / Tools** | Markdown | Minimal `AGENTS.md` pointing to `SKILL.md` | In-skill root |

## Wrapper Specifications

### 1. `AGENTS.md` (Markdown Fallback)
For agent harnesses that look for a root `AGENTS.md` file without parsing YAML frontmatter:
```markdown
# <Skill Title>

<Description>

For the canonical instructions, workflows, references, and executable scripts, see [SKILL.md](./SKILL.md).
```

### 2. `agents/openai.yaml` (OpenAI Codex Metadata)
For OpenAI Codex skill interfaces requiring UI display strings:
```yaml
interface:
  display_name: "<Skill Title>"
  short_description: "<Short Description>"
```

The installer (`scripts/install.sh`) and validator (`scripts/validate.py`) ensure that any skill created automatically maintains these minimal wrappers without author burden.
