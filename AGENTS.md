# AGENTS.md

This repository is governed by the Engineering Knowledge Base (KB).
The KB is the source of truth for standards, workflows, and required
artifacts.

## Required behavior

- Read `AI_CONTEXT.md`, `.kb/ai-context.yaml`, and `PLANS.md` before
  any design, spec, or code changes (STD-056 section 4).
- Read `PLANS.md` to determine ExecPlan requirements.
- Retrieve and cite relevant KB standards and workflows.
- Use approved templates and follow the SDLC stages in
  [SDLC_With_AI](https://github.com/sh4i-yurei/policies-and-standards/blob/main/05_Dev_Workflows/SDLC_With_AI.md).
- When work is complex (Tier 3, cross-module, multi-day, or high-risk),
  require an ExecPlan as defined in `PLANS.md`.
- Use the `repo-orientation` skill when starting a new task or when repo
  context is unclear.
- Repo-local skills live in `.claude/skills/<skill-name>/SKILL.md`;
  use them when they match the task.
- If a required standard or template is missing, stop and request a KB
  update.
- Use `/usr/local/sbin/codex-helper.sh` for privileged operations; do
  not run raw `sudo`.

## Git safety

- Chain `git branch --show-current &&` before every commit and push.
  Shell state does not persist between tool calls — never trust a
  prior call's working directory or branch.
- Never push to main. All changes go through PRs.
- In multi-instance sessions, only touch branches you own. If the
  session handoff lists branch ownership, respect it.

## Artifact creation

- Before creating any governed artifact (session review, ExecPlan,
  ADR, design doc), fetch its template from `06_Projects/Templates/`
  in the KB. Do not improvise the format.
- Before writing any CI or config fix, read the actual error output
  first. Do not guess.

## Problem solving

- Diagnose root causes before proposing solutions. Only suggest
  workarounds if the root cause cannot be fixed.

## Project-specific rules

- This is a Tier 3 project in specification phase (Stage 3). Do not
  write implementation code until technical specs and schema definitions
  are approved.
- Python package name is `engram` (not `3ngram`).
- All design documents must follow KB templates from
  policies-and-standards.
- Architecture decisions require ADRs and Quint tracking.

## Repository AI artifacts

- `AI_CONTEXT.md` (context pack — standards, rule packs, key files)
- `.kb/ai-context.yaml` (KB reference and pinning)
- `PLANS.md` (ExecPlan criteria and session progress)
- `.claude/skills/<skill-name>/SKILL.md` (repo-local skills)

## KB reference

- KB source: <https://github.com/sh4i-yurei/policies-and-standards>
- KB reference: v2.0.0
- Applicable standards: see `.kb/ai-context.yaml`

## PR expectations

- Use `.github/pull_request_template.md` and include KB citations.
- Summarize AI assistance and validation performed.
