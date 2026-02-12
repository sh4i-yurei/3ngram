---
name: repo-orientation
description: Map repo structure and governing docs; use when starting a new task or repo.
---

# Overview

Provide a read-only orientation to the 3ngram repository, including
required governance artifacts and ExecPlan requirements.

# Instructions

- Read `AGENTS.md` for repo-specific AI rules and constraints.
- Read `PLANS.md` to determine whether an ExecPlan is required.
- Read `.kb/ai-context.yaml` for KB pointers and required artifacts.
- Locate core project artifacts (README, charter, PRD, designs, specs,
  ADRs, risk register, testing strategy, style guide, release/ops docs).
- Identify primary source, test, docs, config, and script directories.
- Note any repo-local skills in `.claude/skills` and rule packs
  referenced by the KB.
- Output a short orientation summary:
  - ExecPlan required (yes/no + reason).
  - Key docs found (with paths).
  - Repo structure (source/tests/docs/config).
  - Missing artifacts or questions to resolve.

# Safety / Limits

- Read-only: do not edit files or run commands unless explicitly asked.
- Do not infer missing requirements; ask for clarification.
