#!/usr/bin/env bash
# Wrapper for markdownlint-cli2 using system-installed node.
# Used by pre-commit to avoid nvm lazy-load issues.
set -euo pipefail
export PATH="/home/mark/.nvm/versions/node/v24.11.0/bin:$PATH"
exec markdownlint-cli2 "$@"
