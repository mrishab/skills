#!/usr/bin/env python3
"""
Validation and linting tool for mrishab/skills repository.
Ensures all skills comply with the open Agent Skills standard and verifies
minimal agent wrappers, link integrity, frontmatter schema, and executable permissions.
"""

import os
import re
import sys
import argparse
from pathlib import Path

# ANSI colors
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BLUE = "\033[94m"
BOLD = "\033[1m"
RESET = "\033[0m"


def parse_frontmatter(content: str) -> tuple[dict, str]:
    """Parse YAML frontmatter between triple dashes ---."""
    if not content.startswith("---"):
        return {}, content
    
    parts = content.split("---", 2)
    if len(parts) < 3:
        return {}, content
    
    fm_raw = parts[1].strip()
    body = parts[2]
    
    data = {}
    current_key = None
    multiline_val = []

    for line in fm_raw.splitlines():
        # Handle multiline string indicator >- or |
        if current_key and (line.startswith("  ") or line.startswith("\t")):
            multiline_val.append(line.strip())
            continue
        elif current_key and multiline_val:
            data[current_key] = " ".join(multiline_val)
            current_key = None
            multiline_val = []

        if ":" in line:
            key, val = line.split(":", 1)
            key = key.strip()
            val = val.strip()
            if val in (">-", ">", "|", "|-"):
                current_key = key
                multiline_val = []
            elif val.startswith('"') and val.endswith('"'):
                data[key] = val[1:-1]
            elif val.startswith("'") and val.endswith("'"):
                data[key] = val[1:-1]
            else:
                data[key] = val

    if current_key and multiline_val:
        data[current_key] = " ".join(multiline_val)

    return data, body


def generate_wrappers(skill_dir: Path, name: str, description: str, title: str):
    """Generate minimal AGENTS.md and agents/openai.yaml wrappers pointing to SKILL.md."""
    # 1. AGENTS.md wrapper
    agents_md = skill_dir / "AGENTS.md"
    agents_content = (
        f"# {title}\n\n"
        f"{description}\n\n"
        "For the canonical instructions, workflows, references, and executable scripts, "
        "see [SKILL.md](./SKILL.md).\n"
    )
    agents_md.write_text(agents_content, encoding="utf-8")

    # 2. agents/openai.yaml wrapper
    agents_subdir = skill_dir / "agents"
    agents_subdir.mkdir(exist_ok=True)
    openai_yaml = agents_subdir / "openai.yaml"
    clean_desc = description.replace('"', '\\"').split("\n")[0].strip()
    if len(clean_desc) > 120:
        clean_desc = clean_desc[:117].rsplit(" ", 1)[0] + "..."
    openai_content = (
        "interface:\n"
        f'  display_name: "{title}"\n'
        f'  short_description: "{clean_desc}"\n'
    )
    openai_yaml.write_text(openai_content, encoding="utf-8")


def validate_skill(skill_dir: Path, fix: bool = False) -> list[str]:
    """Validate a single skill directory."""
    errors = []
    skill_name = skill_dir.name

    # Check kebab-case
    if not re.match(r"^[a-z0-9]+(-[a-z0-9]+)*$", skill_name):
        errors.append(f"Directory name '{skill_name}' must be lowercase kebab-case (e.g., 'my-skill').")

    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        errors.append("Missing required 'SKILL.md' file.")
        return errors

    content = skill_md.read_text(encoding="utf-8")
    frontmatter, body = parse_frontmatter(content)

    if not frontmatter:
        errors.append("SKILL.md is missing YAML frontmatter (enclosed by '---').")
        return errors

    # Validate name
    fm_name = frontmatter.get("name")
    if not fm_name:
        errors.append("Frontmatter missing required 'name' property.")
    elif fm_name != skill_name:
        errors.append(f"Frontmatter 'name' ('{fm_name}') does not match directory name ('{skill_name}').")

    # Validate description
    description = frontmatter.get("description", "").strip()
    if not description:
        errors.append("Frontmatter missing required 'description' property or it is empty.")
    elif len(description) < 20:
        errors.append(f"Description is too short ({len(description)} chars). Please provide clear trigger criteria.")

    # Validate Markdown links in SKILL.md
    link_pattern = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
    for match in link_pattern.finditer(body):
        link_target = match.group(2).split("#")[0].strip()
        # Only validate local relative paths
        if link_target and not link_target.startswith(("http://", "https://", "mailto:", "file://", "#")):
            target_path = (skill_dir / link_target).resolve()
            if not target_path.exists():
                errors.append(f"Broken relative link in SKILL.md: '{link_target}' (resolved to {target_path})")

    # Validate script permissions
    scripts_dir = skill_dir / "scripts"
    if scripts_dir.is_dir():
        for script_file in scripts_dir.iterdir():
            if script_file.is_file() and not script_file.name.startswith("."):
                # Check shebang
                try:
                    with open(script_file, "rb") as f:
                        first_line = f.readline().decode("utf-8", errors="ignore")
                        if not first_line.startswith("#!"):
                            errors.append(f"Script '{script_file.name}' is missing a valid shebang (e.g., #!/usr/bin/env bash).")
                except Exception as e:
                    errors.append(f"Failed to read script '{script_file.name}': {e}")

                # Check executable bit
                if not os.access(script_file, os.X_OK):
                    if fix:
                        script_file.chmod(script_file.stat().st_mode | 0o111)
                    else:
                        errors.append(f"Script '{script_file.name}' is not marked executable. Run: chmod +x '{script_file}'")

    # Validate or generate minimal agent wrappers
    title = frontmatter.get("name", skill_name).replace("-", " ").title()
    agents_md = skill_dir / "AGENTS.md"
    openai_yaml = skill_dir / "agents" / "openai.yaml"

    if fix and description and fm_name:
        generate_wrappers(skill_dir, fm_name, description, title)
    else:
        if not agents_md.exists():
            errors.append("Missing minimal fallback 'AGENTS.md' wrapper. Run with --fix to generate.")
        if not openai_yaml.exists():
            errors.append("Missing minimal 'agents/openai.yaml' wrapper for Codex. Run with --fix to generate.")

    return errors


def main():
    parser = argparse.ArgumentParser(description="Validate agent skills against open standards.")
    parser.add_argument("--skills-dir", default="skills", help="Directory containing skills (default: skills)")
    parser.add_argument("--templates-dir", default="templates", help="Directory containing skill templates")
    parser.add_argument("--fix", action="store_true", help="Auto-fix missing wrappers and executable permissions")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent.parent
    skills_root = repo_root / args.skills_dir
    templates_root = repo_root / args.templates_dir

    print(f"{BOLD}{BLUE}=== Validating Skills in {skills_root} ==={RESET}\n")

    all_passed = True
    skills_found = 0

    target_dirs = []
    if skills_root.exists():
        target_dirs.extend([d for d in skills_root.iterdir() if d.is_dir() and not d.name.startswith(".")])
    if templates_root.exists():
        target_dirs.extend([d for d in templates_root.iterdir() if d.is_dir() and not d.name.startswith(".")])

    if not target_dirs:
        print(f"{YELLOW}No skills found to validate in {skills_root}.{RESET}")
        return 0

    for s_dir in sorted(target_dirs, key=lambda p: p.name):
        skills_found += 1
        errs = validate_skill(s_dir, fix=args.fix)
        if errs:
            all_passed = False
            print(f"[{RED}FAIL{RESET}] {BOLD}{s_dir.name}{RESET}")
            for err in errs:
                print(f"  {RED}✖{RESET} {err}")
        else:
            print(f"[{GREEN}PASS{RESET}] {BOLD}{s_dir.name}{RESET}")

    print()
    if all_passed:
        print(f"{GREEN}{BOLD}✔ All {skills_found} skill(s) passed validation!{RESET}")
        return 0
    else:
        print(f"{RED}{BOLD}✖ Validation failed. Review errors above or run with --fix.{RESET}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
