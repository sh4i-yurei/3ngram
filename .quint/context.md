# Bounded Context

## Vocabulary

CI gates, reusable workflows, STD-030, Gate A (quint), Gate B (docs), Gate C (code), Gate D (tests), Gate E (config), Gate F (security), cspell, policies-and-standards

## Invariants

All PRs to main must pass CI gates A-F per STD-030. Gate A requires .quint/ artifacts updated in every code PR. Reusable workflows called from policies-and-standards repo. No direct pushes to main — PR-based workflow only.
