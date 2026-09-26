# Agent Wrappers Architecture

Wrappers provide minimal shims for harnesses that do not natively parse `SKILL.md`.

## Supported Harnesses

| Harness | Native Support | Wrapper | Global Target |
| :--- | :--- | :--- | :--- |
| **Claude Code** | Native (`SKILL.md`) | None (direct symlink) | `~/.claude/skills/<skill>` |
| **Google Antigravity** | Native (`SKILL.md`) | None (direct symlink) | `~/.gemini/config/skills/<skill>` |
| **OpenCode** | Native (`SKILL.md`) | None (direct symlink) | `~/.config/opencode/skills/<skill>` |
| **OpenAI Codex** | Partial | `agents/openai.yaml` + `AGENTS.md` | `~/.codex/skills/<skill>` |
| **Cursor** | Partial | `AGENTS.md` | `~/.cursor/skills/<skill>` |

## Wrapper Formats

### `AGENTS.md`
Fallback pointer for markdown-only harnesses:
```markdown
# <Skill Title>
<Description>
For canonical instructions and workflows, see [SKILL.md](./SKILL.md).
```

### `agents/openai.yaml`
Codex UI display metadata:
```yaml
interface:
  display_name: "<Skill Title>"
  short_description: "<Short Description>"
```

Wrappers are auto-generated via `make fix`.
