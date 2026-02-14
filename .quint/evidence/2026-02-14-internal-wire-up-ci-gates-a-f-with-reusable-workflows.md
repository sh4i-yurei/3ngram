---
target: wire-up-ci-gates-a-f-with-reusable-workflows
verdict: pass
assurance_level: L2
carrier_ref: test-runner
valid_until: 2026-05-15
date: 2026-02-14
id: 2026-02-14-internal-wire-up-ci-gates-a-f-with-reusable-workflows.md
type: internal
content_hash: 81239dc65269da72254f7a218e9d1a8c
---

# Evidence: CI gates validation

CI run 22014351382: Gates B-F all pass, cspell passes. Gate A fails only because .quint/ not yet updated in this PR (chicken-and-egg — this quint recording fixes it). Upstream bugs resolved: pipefail in Gate E (p-a-s #17), broken links (PRs #15, #16), dependency graph (repo made public). mlc_config.json adopted from PR #18 with targeted URL ignores.
