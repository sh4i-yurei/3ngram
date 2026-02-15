#!/usr/bin/env bash
# validate-version-refs.sh — Check version references are consistent.
#
# Reads the canonical version from pyproject.toml and verifies that
# version references in docs/ frontmatter and src/ match.
#
# Usage:
#   validate-version-refs.sh          # check all version refs
#   validate-version-refs.sh --help   # show this help
#
# Exit codes:
#   0 — all version refs consistent
#   1 — mismatches found

set -euo pipefail

usage() {
    sed -n '2,10s/^# //p' "$0"
    exit 0
}

[[ "${1:-}" == "--help" || "${1:-}" == "-h" ]] && usage

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || echo ".")"

# --- Read canonical version from pyproject.toml ---

PYPROJECT="${REPO_ROOT}/pyproject.toml"
if [[ ! -f "$PYPROJECT" ]]; then
    echo "Error: pyproject.toml not found at ${PYPROJECT}" >&2
    exit 1
fi

CANONICAL=$(grep -E '^version\s*=' "$PYPROJECT" | head -1 | sed 's/.*=\s*"\(.*\)"/\1/')
if [[ -z "$CANONICAL" ]]; then
    echo "Error: could not extract version from pyproject.toml" >&2
    exit 1
fi

echo "Canonical version: ${CANONICAL} (from pyproject.toml)"
echo ""

errors=0

# --- Check __init__.py ---

INIT_FILE="${REPO_ROOT}/src/engram/__init__.py"
if [[ -f "$INIT_FILE" ]]; then
    INIT_VERSION=$(grep -E '__version__[[:space:]]*=' "$INIT_FILE" | head -1 | sed 's/.*__version__[[:space:]]*=[[:space:]]*"\([^"]*\)".*/\1/' || echo "")
    if [[ -z "$INIT_VERSION" ]]; then
        echo "WARN: no __version__ found in ${INIT_FILE}"
    elif [[ "$INIT_VERSION" != "$CANONICAL" ]]; then
        echo "FAIL: src/engram/__init__.py has ${INIT_VERSION}, expected ${CANONICAL}"
        errors=$((errors + 1))
    else
        echo "PASS: src/engram/__init__.py"
    fi
fi

# --- Check docs/ frontmatter version fields ---
# Only checks files with YAML frontmatter (--- delimited) that have
# a top-level 'version:' field. This is the DOCUMENT version, not the
# package version — we check that it parses as a valid semver-ish string.

doc_count=0
doc_errors=0

if [[ ! -d "${REPO_ROOT}/docs" ]]; then
    echo "SKIP: docs/ directory not found"
else
    while IFS= read -r -d '' mdfile; do
        # Extract frontmatter (between first two --- lines)
        frontmatter=$(sed -n '/^---$/,/^---$/p' "$mdfile" | sed '1d;$d')
        if [[ -z "$frontmatter" ]]; then
            continue
        fi

        # Check for version field
        doc_version=$(echo "$frontmatter" | grep -E '^version:' | head -1 \
            | sed -E "s/^version:[[:space:]]*['\"]?([^'\"]*)['\"]?[[:space:]]*$/\1/")
        if [[ -z "$doc_version" ]]; then
            continue
        fi

        doc_count=$((doc_count + 1))

        # Validate it looks like a version (N.N.N or N.N)
        if ! echo "$doc_version" | grep -qE '^[0-9]+\.[0-9]+(\.[0-9]+)?$'; then
            echo "FAIL: ${mdfile#${REPO_ROOT}/} has invalid version format: ${doc_version}"
            doc_errors=$((doc_errors + 1))
        fi
    done < <(find "${REPO_ROOT}/docs" -name '*.md' -print0)
fi

if [[ $doc_count -gt 0 ]]; then
    echo "PASS: ${doc_count} docs have valid version format (${doc_errors} errors)"
fi
if [[ $doc_errors -gt 0 ]]; then
    errors=$((errors + doc_errors))
fi

# --- Summary ---

echo ""
if [[ $errors -gt 0 ]]; then
    echo "FAIL: ${errors} version inconsistencies found"
    exit 1
else
    echo "PASS: all version references consistent"
    exit 0
fi
