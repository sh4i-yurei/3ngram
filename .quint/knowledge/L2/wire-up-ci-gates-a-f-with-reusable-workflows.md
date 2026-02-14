---
scope: CI/CD pipeline configuration for 3ngram repository
kind: system
content_hash: 1a063365eac1b9536749211beba3ac99
---

# Hypothesis: Wire up CI gates A-F with reusable workflows

Configure .github/workflows/ci.yml to call all 6 reusable gate workflows from policies-and-standards per STD-030. Add standalone cspell job for spell checking (not yet in upstream Gate B). Remove redundant test_placeholder.py in favor of test_smoke.py which validates package import.

## Rationale

{"anomaly": "CI gates A-F defined in STD-030 but only enforced locally via pre-commit hooks. No automated CI validation on PRs.", "approach": "Call reusable gate workflows from policies-and-standards@main. Gate A enabled after .quint/ committed (3ngram PR #18). Add cspell as local job until upstream Gate B includes it.", "alternatives_rejected": "Inline gate logic in ci.yml — rejected because reusable workflows maintain single source of truth in KB repo."}
