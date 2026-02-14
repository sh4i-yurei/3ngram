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

CI run 22014410930: All gates pass (A-F + cspell). Gate A initially failed on run 22014351382 because .quint/ artifacts had not yet been added; this PR includes the corresponding quint recording and Gate A now passes. Upstream bugs resolved: pipefail in Gate E (policies-and-standards #17), broken links (3ngram PRs #15, #16), dependency graph (repo made public). mlc_config.json adopted from 3ngram PR #18 with targeted URL ignores.
