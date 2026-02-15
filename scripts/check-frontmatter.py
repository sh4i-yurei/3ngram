#!/usr/bin/env python3
"""check-frontmatter.py — Validate YAML frontmatter in governed docs.

Checks that markdown files under docs/ have required frontmatter fields
per KB governance standards. Python stdlib only — no external deps.

Usage:
    check-frontmatter.py                    # check all docs/
    check-frontmatter.py docs/design/       # check specific directory
    check-frontmatter.py --help             # show this help

Exit codes:
    0 — all files pass
    1 — validation errors found
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# Required frontmatter fields for governed documents.
REQUIRED_FIELDS = {"id", "title", "version", "status", "last_updated"}

# Valid status values.
VALID_STATUSES = {
    "draft",
    "active",
    "approved",
    "deprecated",
    "superseded",
    "accepted",  # ADR-specific status per STD-047
}

# Validation patterns for specific fields.
VERSION_PATTERN = re.compile(r"^\d+\.\d+(\.\d+)?$")
DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def extract_frontmatter(text: str) -> dict[str, str] | None:
    """Extract YAML frontmatter from markdown text.

    Returns a dict of key-value pairs, or None if no frontmatter found.
    Only handles simple key: value pairs (not nested YAML).
    """
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    if not match:
        return None

    fields: dict[str, str] = {}
    for line in match.group(1).splitlines():
        m = re.match(r"^(\w[\w_]*)\s*:\s*(.+)$", line)
        if m:
            fields[m.group(1)] = m.group(2).strip()
    return fields


def _strip_quotes(value: str) -> str:
    return value.strip("\"'")


def _check_required_fields(
    fm: dict[str, str],
    rel: str,
) -> list[str]:
    return [
        f"{rel}: missing required field '{f}'" for f in REQUIRED_FIELDS if f not in fm
    ]


def _check_field_formats(
    fm: dict[str, str],
    rel: str,
) -> list[str]:
    errors: list[str] = []
    if "version" in fm and not VERSION_PATTERN.match(_strip_quotes(fm["version"])):
        errors.append(f"{rel}: invalid version format '{fm['version']}'")
    if "status" in fm and _strip_quotes(fm["status"]).lower() not in VALID_STATUSES:
        valid = ", ".join(sorted(VALID_STATUSES))
        errors.append(f"{rel}: invalid status '{fm['status']}' (expected: {valid})")
    date_raw = fm.get("last_updated", "")
    if date_raw and not DATE_PATTERN.match(_strip_quotes(date_raw)):
        errors.append(
            f"{rel}: invalid date '{date_raw}' (expected YYYY-MM-DD)",
        )
    return errors


def validate_file(filepath: Path) -> list[str]:
    """Validate a single markdown file. Returns list of error messages."""
    rel = filepath.as_posix()

    try:
        text = filepath.read_text(encoding="utf-8")
    except OSError as e:
        return [f"{rel}: cannot read file: {e}"]

    fm = extract_frontmatter(text)
    if fm is None:
        return [f"{rel}: missing YAML frontmatter"]

    return _check_required_fields(fm, rel) + _check_field_formats(fm, rel)


def _collect_files(target: Path) -> list[Path]:
    files = [target] if target.is_file() else sorted(target.rglob("*.md"))
    return [
        f
        for f in files
        if "template" not in f.name.lower() and not f.name.startswith(".")
    ]


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate YAML frontmatter in governed markdown docs.",
    )
    parser.add_argument(
        "path",
        nargs="?",
        default="docs",
        help="Directory or file to check (default: docs/)",
    )
    args = parser.parse_args()
    target = Path(args.path)

    if not target.exists():
        print(f"Error: {target} does not exist", file=sys.stderr)
        sys.exit(1)

    files = _collect_files(target)
    if not files:
        print(f"No markdown files found in {target}")
        sys.exit(0)

    all_errors: list[str] = []
    checked = 0
    for f in files:
        errors = validate_file(f)
        text = f.read_text(encoding="utf-8")
        if errors or extract_frontmatter(text) is not None:
            checked += 1
        all_errors.extend(errors)

    print(f"Checked {checked} governed docs in {target}")
    if all_errors:
        print(f"\n{len(all_errors)} errors found:\n")
        for err in all_errors:
            print(f"  {err}")
        sys.exit(1)
    print("All frontmatter valid.")


if __name__ == "__main__":
    main()
