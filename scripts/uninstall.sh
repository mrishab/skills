#!/usr/bin/env bash
# Quick uninstaller wrapper for mrishab/skills
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
"${SCRIPT_DIR}/install.sh" --uninstall "$@"
