---
id: TPL-PRJ-AGENTS
title: AGENTS.md template
version: 0.2.0
category: project
status: active
owner: sh4i-yurei
reviewer: sh4i-yurei
approver: sh4i-yurei
last_updated: 2026-02-12
extends: [STD-001, STD-004, STD-056]
tags: [template, ai, agents, kb, governance]
---
# Purpose

Provide a repo-local AGENTS.md file that tells AI systems how to use the
knowledge base (KB) as the source of truth.

# Scope

Use in all governed repositories. Save as `AGENTS.md` at the repo root.

# Standard

## Template

### AGENTS.md

This repository is governed by the Engineering Knowledge Base (KB).
The KB is the source of truth for standards, workflows, and required
artifacts.

Required behavior:

- Read the KB [INDEX.md](../../../INDEX.md) for the full document registry
  before searching for standards or templates.
- Read the KB [Onboarding](../../../00_Orientation/Onboarding.md) for the
  governance reading path and KB structure.
- Read `.kb/ai-context.yaml` before any design, spec, or code changes.
- Read `PLANS.md` to determine ExecPlan requirements.
- Read `AI_CONTEXT.md` (context pack) for task context.
- Retrieve and cite relevant KB standards and workflows.
- Use approved templates and follow the SDLC stages in [SDLC_With_AI](../../../05_Dev_Workflows/SDLC_With_AI.md).
- When work is complex (Tier 3, cross-module, multi-day, or high-risk),
  require an ExecPlan as defined in `PLANS.md`.
- Use the `repo-orientation` skill when starting a new task or when repo
  context is unclear.
- Repo-local skills live in `.claude/skills/<skill-name>/SKILL.md`;
  use them when they match the task.
- If a required standard or template is missing, stop and request a KB
  update.
- Repository-specific overrides apply only when explicitly stated in
  `.kb/ai-context.yaml`.
- Use `/usr/local/sbin/codex-helper.sh` for privileged operations; do
  not run raw `sudo`. Request helper updates for new privileged actions.

Repository AI artifacts:

- `.kb/ai-context.yaml` (KB reference and applicable standards)
- `AI_CONTEXT.md` (context pack)
- `PLANS.md` (ExecPlan criteria)
- `.claude/skills/<skill-name>/SKILL.md` (repo-local skills)

KB reference:

- KB source: <link or path>
- KB reference: <tag or branch>
- Applicable standards: <list or "see .kb/ai-context.yaml">

PR expectations:

- Use `.github/pull_request_template.md` and include KB citations.
- Summarize AI assistance and validation performed.

# Implementation Notes

- Keep AGENTS.md short and action-oriented.

# Continuous Improvement and Compliance Metrics

- Track AI requests that lack KB citations.

# Compliance

Repositories without AGENTS.md are non-compliant.

# Changelog

- 0.2.0 - Added KB INDEX.md and Onboarding as required agent reading.
- 0.1.9 - Normalized skill paths to Claude Code as primary runtime.
- 0.1.8 - Updated skill paths to support both Claude Code and Codex runtimes.
- 0.1.7 - Set owner/reviewer/approver values.
- 0.1.6 - Added owner/reviewer/approver frontmatter fields.

- 0.1.5 - Added explicit AI artifact locations.
- 0.1.4 - Added context pack, PLANS, and repo-orientation guidance.
- 0.1.3 - Required use of repo-local skills when applicable.
- 0.1.2 - Added ExecPlan requirement for complex work.
- 0.1.1 - Added sudo-helper requirement.
- 0.1.0 - Initial draft.
