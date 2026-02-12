# 3ngram

A kernel-governed memory OS for AI agents. Typed, versioned memory with
agentic retrieval, policy-gated durable writes, and dual-protocol
communication (MCP + A2A).

## Motivation

LLMs are fundamentally amnesic — fixed context windows, no durable state,
hallucinations when retrieval fails. Existing RAG solutions treat memory
as a library concern. 3ngram treats memory as an OS-level kernel with
mandatory invariants, typed memory, and self-healing mechanisms.

This project replaces the deprecated `ai_tech_stack` repository, applying
lessons learned from that attempt.

## Status

**Tier 3 design phase** — all architecture and design artifacts are being
produced before any implementation code is written.

See `PLANS.md` for current progress and `docs/` for design artifacts.

## Architecture overview

(Design in progress — see `docs/design/system-design.md` when available)

Core concepts:

- **Memory Kernel**: Typed records (Decision, Belief, Episode, Skill) with
  temporal awareness and versioning
- **Agentic Retrieval**: 6-stage pipeline with hybrid search, validation,
  and bounded retries
- **Librarian Gate**: No durable memory write without policy authorization
- **Dual Protocol**: MCP (agent-to-tools) + A2A v0.3 (agent-to-agent)
- **Monolith-first**: Single Python service with clear module boundaries

## Quick start

Prerequisites and setup instructions will be added after the design
phase completes.

## Development workflow

- Branch strategy: `<type>/<short-name>`, squash merge, PR-based
- AI assistance governed by `AGENTS.md` and `.kb/ai-context.yaml`
- CI gates A-F per STD-030

## Testing

Testing strategy and commands will be added after specification phase.

## Documentation

- [Project Intake](docs/planning/project-intake.md)
- [Project Proposal](docs/planning/project-proposal.md)
- [AGENTS.md](AGENTS.md) — AI agent behavior rules
- [PLANS.md](PLANS.md) — ExecPlan requirements and progress

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) and
[CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).
