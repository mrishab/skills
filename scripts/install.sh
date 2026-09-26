#!/usr/bin/env bash
# Universal Multi-Agent Skills Installer
# Installs skills from mrishab/skills into Claude Code, Antigravity, OpenCode, Codex, Cursor, etc.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
SKILLS_DIR="${REPO_ROOT}/skills"

# ANSI Colors
GREEN="\033[92m"
YELLOW="\033[93m"
RED="\033[91m"
BLUE="\033[94m"
CYAN="\033[96m"
BOLD="\033[1m"
RESET="\033[0m"

# Default configuration
AGENT="all"
SKILL_TARGET="all"
MODE="symlink"
SCOPE="global"
PROJECT_DIR=""
ACTION="install"
FORCE=false

usage() {
  cat <<EOF
${BOLD}mrishab/skills Universal Agent Installer${RESET}

${BOLD}USAGE:${RESET}
  ./scripts/install.sh [OPTIONS]

${BOLD}OPTIONS:${RESET}
  -a, --agent <name>       Target agent harness:
                           claude, antigravity, opencode, codex, cursor, all (default: all)
  -s, --skill <name>       Specific skill to install or 'all' (default: all)
  -m, --mode <mode>        Install mode: 'symlink' or 'copy' (default: symlink)
  -g, --global             Install globally to user agent directories (default)
  -p, --project <path>     Install locally into a target project repository
      --status             Show current installation status across agents
      --uninstall          Remove installed skills from agent directories
  -f, --force              Overwrite existing targets without prompt
  -h, --help               Display this help message

${BOLD}EXAMPLES:${RESET}
  ./scripts/install.sh --agent all                 # Install all skills to all global agents
  ./scripts/install.sh --agent claude              # Install all skills to Claude Code
  ./scripts/install.sh --skill mobile-native-feel  # Install single skill to all agents
  ./scripts/install.sh --project ~/SourceCode/my-app # Install into project repo
  ./scripts/install.sh --status                    # Check installation status
  ./scripts/install.sh --uninstall --agent codex   # Uninstall from Codex
EOF
  exit 0
}

# Parse flags
while [[ $# -gt 0 ]]; do
  case "$1" in
    -a|--agent) AGENT="$2"; shift 2 ;;
    -s|--skill) SKILL_TARGET="$2"; shift 2 ;;
    -m|--mode) MODE="$2"; shift 2 ;;
    -g|--global) SCOPE="global"; shift ;;
    -p|--project) SCOPE="project"; PROJECT_DIR="$2"; shift 2 ;;
    --status|--list) ACTION="status"; shift ;;
    --uninstall) ACTION="uninstall"; shift ;;
    -f|--force) FORCE=true; shift ;;
    -h|--help) usage ;;
    *) echo -e "${RED}Unknown option: $1${RESET}" >&2; usage ;;
  esac
done

# Resolve Agent Directory Paths
get_agent_dir() {
  local agent="$1"
  local scope="$2"
  local base_dir="${PROJECT_DIR:-$(pwd)}"

  if [[ "$scope" == "global" ]]; then
    case "$agent" in
      claude) echo "${HOME}/.claude/skills" ;;
      antigravity) echo "${HOME}/.gemini/config/skills" ;;
      opencode) echo "${HOME}/.config/opencode/skills" ;;
      codex) echo "${HOME}/.codex/skills" ;;
      cursor) echo "${HOME}/.cursor/skills" ;;
      *) echo "" ;;
    esac
  else
    case "$agent" in
      claude) echo "${base_dir}/.claude/skills" ;;
      antigravity) echo "${base_dir}/.agents/skills" ;;
      opencode) echo "${base_dir}/.opencode/skills" ;;
      codex) echo "${base_dir}/.codex/skills" ;;
      cursor) echo "${base_dir}/.cursor/skills" ;;
      *) echo "" ;;
    esac
  fi
}

AVAILABLE_AGENTS=("claude" "antigravity" "opencode" "codex" "cursor")

# Get list of skills to process
get_skills_list() {
  if [[ ! -d "$SKILLS_DIR" ]]; then
    echo ""
    return
  fi
  if [[ "$SKILL_TARGET" == "all" ]]; then
    find "$SKILLS_DIR" -mindepth 1 -maxdepth 1 -type d ! -name ".*" -exec basename {} \;
  else
    if [[ -d "${SKILLS_DIR}/${SKILL_TARGET}" ]]; then
      echo "$SKILL_TARGET"
    else
      echo -e "${RED}Skill '${SKILL_TARGET}' not found in ${SKILLS_DIR}.${RESET}" >&2
      exit 1
    fi
  fi
}

# Ensure minimal wrappers exist for all skills prior to install
ensure_wrappers() {
  python3 "${SCRIPT_DIR}/validate.py" --fix >/dev/null 2>&1 || true
}

# Action: Status
show_status() {
  echo -e "\n${BOLD}${BLUE}=== Agent Skills Installation Status ===${RESET}"
  echo -e "Skills Source: ${BOLD}${SKILLS_DIR}${RESET}\n"

  local skills=($(get_skills_list))
  if [[ ${#skills[@]} -eq 0 ]]; then
    echo -e "${YELLOW}No skills found in ${SKILLS_DIR}.${RESET}\n"
    return
  fi

  for a in "${AVAILABLE_AGENTS[@]}"; do
    local target_dir
    target_dir="$(get_agent_dir "$a" "$SCOPE")"
    echo -e "${BOLD}${CYAN}● Agent: ${a}${RESET} (${target_dir})"

    if [[ ! -d "$target_dir" ]]; then
      echo -e "  ${YELLOW}Directory does not exist (Agent may not be installed).${RESET}"
      continue
    fi

    for s in "${skills[@]}"; do
      local dest="${target_dir}/${s}"
      if [[ -L "$dest" ]]; then
        local link_target
        link_target="$(readlink "$dest")"
        echo -e "  ${GREEN}✔${RESET} ${s} -> [Symlinked] ${link_target}"
      elif [[ -d "$dest" ]]; then
        echo -e "  ${BLUE}●${RESET} ${s} -> [Copied directory]"
      else
        echo -e "  ${RED}✖${RESET} ${s} -> [Not installed]"
      fi
    done
    echo
  done
}

# Action: Uninstall
do_uninstall() {
  echo -e "\n${BOLD}${YELLOW}=== Uninstalling Agent Skills ===${RESET}\n"
  local target_agents=()
  if [[ "$AGENT" == "all" ]]; then
    target_agents=("${AVAILABLE_AGENTS[@]}")
  else
    target_agents=("$AGENT")
  fi

  local skills=($(get_skills_list))

  for a in "${target_agents[@]}"; do
    local target_dir
    target_dir="$(get_agent_dir "$a" "$SCOPE")"
    if [[ ! -d "$target_dir" ]]; then
      continue
    fi

    echo -e "${BOLD}Removing from ${a}...${RESET}"
    for s in "${skills[@]}"; do
      local dest="${target_dir}/${s}"
      if [[ -L "$dest" || -d "$dest" ]]; then
        rm -rf "$dest"
        echo -e "  ${GREEN}✔ Removed ${s} from ${target_dir}${RESET}"
      fi
    done
  done
  echo -e "\n${GREEN}${BOLD}Uninstallation complete.${RESET}\n"
}

# Action: Install
do_install() {
  ensure_wrappers

  echo -e "\n${BOLD}${BLUE}=== Installing Skills for AI Agents ===${RESET}"
  echo -e "Mode:  ${BOLD}${MODE}${RESET}"
  echo -e "Scope: ${BOLD}${SCOPE}${RESET}"
  if [[ "$SCOPE" == "project" ]]; then
    echo -e "Project: ${BOLD}${PROJECT_DIR}${RESET}"
  fi
  echo

  local target_agents=()
  if [[ "$AGENT" == "all" ]]; then
    target_agents=("${AVAILABLE_AGENTS[@]}")
  else
    target_agents=("$AGENT")
  fi

  local skills=($(get_skills_list))
  if [[ ${#skills[@]} -eq 0 ]]; then
    echo -e "${YELLOW}No skills found in ${SKILLS_DIR} to install.${RESET}"
    echo -e "Create a new skill using: ${BOLD}./scripts/new-skill.sh <name>${RESET}"
    return
  fi

  for a in "${target_agents[@]}"; do
    local target_dir
    target_dir="$(get_agent_dir "$a" "$SCOPE")"
    mkdir -p "$target_dir"
    echo -e "${BOLD}${CYAN}Installing for ${a} (${target_dir})...${RESET}"

    for s in "${skills[@]}"; do
      local src="${SKILLS_DIR}/${s}"
      local dest="${target_dir}/${s}"

      if [[ -e "$dest" || -L "$dest" ]]; then
        if [[ "$FORCE" == true ]]; then
          rm -rf "$dest"
        else
          # If already symlinked to this src, skip
          if [[ -L "$dest" && "$(readlink "$dest")" == "$src" ]]; then
            echo -e "  ${GREEN}✔${RESET} ${s} (Already linked)"
            continue
          fi
          rm -rf "$dest"
        fi
      fi

      if [[ "$MODE" == "symlink" ]]; then
        ln -sf "$src" "$dest"
        echo -e "  ${GREEN}✔ Linked${RESET} ${s} -> ${dest}"
      else
        cp -R "$src" "$dest"
        echo -e "  ${GREEN}✔ Copied${RESET} ${s} -> ${dest}"
      fi
    done
    echo
  done

  echo -e "${GREEN}${BOLD}✔ All selected skills successfully installed!${RESET}"
  echo -e "Changes in this repository will automatically reflect in your agents.\n"
}

case "$ACTION" in
  status) show_status ;;
  uninstall) do_uninstall ;;
  install) do_install ;;
esac
