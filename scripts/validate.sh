#!/usr/bin/env bash
# Shell entrypoint for skill validation
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python3 "${SCRIPT_DIR}/validate.py" "$@"
