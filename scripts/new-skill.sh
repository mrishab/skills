#!/usr/bin/env bash
# Scaffold a new skill following the open Agent Skills standard
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
TEMPLATE_DIR="${REPO_ROOT}/templates/skill-template"
SKILLS_DIR="${REPO_ROOT}/skills"

SKILL_NAME="${1:-}"
DESCRIPTION="${2:-}"

# Interactive prompt if name not provided
if [[ -z "$SKILL_NAME" ]]; then
  echo -e "\033[1;34m=== Scaffold a New Agent Skill ===\033[0m"
  read -rp "Skill name (lowercase-kebab-case, e.g. nextjs-debugger): " SKILL_NAME
fi

# Clean and validate name
SKILL_NAME="$(echo "${SKILL_NAME}" | tr '[:upper:]' '[:lower:]' | tr ' _' '--' | tr -cd 'a-z0-9-')"

if [[ -z "$SKILL_NAME" ]]; then
  echo -e "\033[91mError: Skill name cannot be empty.\033[0m" >&2
  exit 1
fi

TARGET_DIR="${SKILLS_DIR}/${SKILL_NAME}"

if [[ -d "$TARGET_DIR" ]]; then
  echo -e "\033[91mError: Skill directory already exists at ${TARGET_DIR}\033[0m" >&2
  exit 1
fi

if [[ -z "$DESCRIPTION" ]]; then
  echo "Enter a clear description of what this skill does and when the agent should use it:"
  read -rp "> " DESCRIPTION
fi

if [[ -z "$DESCRIPTION" ]]; then
  DESCRIPTION="Specialized workflow and procedures for ${SKILL_NAME}. Use when requested to perform tasks related to ${SKILL_NAME}."
fi

mkdir -p "$SKILLS_DIR"
cp -R "$TEMPLATE_DIR" "$TARGET_DIR"

# Generate Title Case Name
TITLE_NAME=$(echo "$SKILL_NAME" | awk -F- '{for(i=1;i<=NF;i++)sub(/./,toupper(substr($i,1,1)),$i)}1')

# Replace placeholders in SKILL.md
python3 - <<EOF
import pathlib

target = pathlib.Path("${TARGET_DIR}/SKILL.md")
content = target.read_text(encoding="utf-8")
content = content.replace("name: skill-template", "name: ${SKILL_NAME}")
content = content.replace("description: A template skill demonstrating the open Agent Skills standard. Use when scaffolding or learning how to write high-quality agent skills.", "description: ${DESCRIPTION}")
content = content.replace("# Skill Template", "# ${TITLE_NAME}")
target.write_text(content, encoding="utf-8")
EOF

# Run validation with --fix to generate minimal wrappers and fix permissions
python3 "${SCRIPT_DIR}/validate.py" --fix

echo
echo -e "\033[92m✔ Successfully created skill at:\033[0m \033[1m${TARGET_DIR}\033[0m"
echo
echo "Next steps:"
echo "  1. Edit ${TARGET_DIR}/SKILL.md with detailed instructions and triggers."
echo "  2. Add reference docs to ${TARGET_DIR}/references/ if needed."
echo "  3. Add helper scripts to ${TARGET_DIR}/scripts/ if needed."
echo "  4. Run 'make validate' or './scripts/validate.sh' to verify."
echo "  5. Install to your agents with 'make install' or './scripts/install.sh --agent all'."
