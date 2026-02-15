---
scope: Code quality infrastructure — pyproject.toml, pre-commit, project scripts
kind: system
content_hash: 37212703217693b9534925bf7f35284d
---

# Hypothesis: Expand ruff rules and add code quality tooling

Add C90 (mccabe), C4 (comprehensions), RET (return), S (bandit security), ARG (unused args), PLR/PLW (pylint) to ruff lint rules. Add vulture for dead code detection and pip-audit for dependency CVE scanning. Create project scripts for version consistency and frontmatter validation.

## Rationale

{"anomaly": "Current ruff rules only cover basic E/F/I/N/W/UP/B/SIM/RUF — missing complexity, security, and pylint checks. No dead code detection or dependency auditing. No version consistency or frontmatter validation scripts.", "approach": "Expand ruff rule set progressively, add vulture + pip-audit as dev deps, create project scripts for CI gate support.", "alternatives_rejected": ["pylint standalone (redundant with ruff PLR/PLW)", "flake8 plugins (ruff subsumes these)", "custom AST-based checks (over-engineering for current needs)"]}
