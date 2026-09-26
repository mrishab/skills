# Authoring & Contributing Skills

This repository houses Rishab Manocha's personal collection of high-value AI agent skills, designed to be maintained centrally and installed across all agents and development environments.

## Development Workflow

### 1. Scaffold a New Skill

Use the built-in scaffolding tool:

```bash
make new NAME=my-new-skill
# Or directly:
./scripts/new-skill.sh my-new-skill "Diagnose and fix issue X. Use when user encounters..."
```

This creates a compliant skill skeleton in `skills/<skill-name>/` with `SKILL.md`, `AGENTS.md`, and `agents/openai.yaml`.

### 2. Author the Instructions

Follow the [Open Agent Skills Specification](./SKILL_SPEC.md):
- Keep `SKILL.md` under ~150-200 lines where possible.
- Put heavy docs or cheatsheets in `references/` and link to them.
- Put scripts in `scripts/` and ensure they have `chmod +x`.

### 3. Validate and Lint

Run the validator before installing or committing:

```bash
make validate
# or
./scripts/validate.sh
```

If any wrappers are missing or permissions need fixing, run:

```bash
make fix
```

### 4. Install Locally to Test with Your Agent

Symlink the new skill to your agent harness:

```bash
# Install to all detected agents:
make install

# Or test specifically with Claude Code:
make install-claude

# Or Google Antigravity:
make install-antigravity
```

Because files are symlinked, edits you make in `skills/<skill-name>/` will be immediately available to your agents!
