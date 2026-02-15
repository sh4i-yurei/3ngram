---
name: schema-authoring
description: Write schema definitions per STD-055. Use when defining data models, API contracts, event formats, or configuration schemas.
---

# Overview

Guide the authoring of Schema Definitions aligned to STD-055 and the
TPL-PRJ-SCHEMA template. Schemas are the canonical source of truth for
data contracts and must be defined before implementation.

# Instructions

## Before writing

1. Confirm a system design or module design exists that references the
   schema being defined.
2. Identify the schema type: data, api, event, config, or layout.
3. Read relevant ADRs that constrain the schema design:
   - ADR-003 (Postgres+pgvector storage)
   - ADR-007 (embedding adapter interface)
   - ADR-009 (knowledge graph edges)
   - ADR-010 (CLS consolidation status)
   - ADR-012 (Librarian Gate audit logging)

## Required elements (STD-055)

1. **Schema summary** -- Name, type, owner, status, version, approver.
2. **Scope and intent** -- What this schema covers and why.
3. **Source of truth** -- Canonical file paths, format/spec used,
   validation tooling, CI integration.
4. **Schema definition** -- Entities, fields, constraints,
   relationships. For API schemas: endpoints, message shapes,
   required fields.
5. **Compatibility and migration** -- Backward/forward compatibility
   rules, migration plan, deprecations.
6. **Consumers and producers** -- Services, modules, or integrations
   that use this schema.
7. **Storage, retention, and privacy** -- Location, retention policy,
   data classification (public/internal/confidential/restricted).
8. **Links** -- System Design, Module Design, Spec, ADRs, Issues/PRs.

## Template reference (TPL-PRJ-SCHEMA)

Canonical template in the KB at:
`06_Projects/Templates/design/schema-definition_tpl.md`

Fetch it with:

```bash
gh api repos/sh4i-yurei/policies-and-standards/contents/06_Projects/Templates/design/schema-definition_tpl.md --jq '.content' | base64 -d
```

## 3ngram-specific: memory record base fields

All memory records share these base fields (from system design v0.1.3):

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| memory_type | ENUM | belief, decision, episode, skill, entity, preference, reflection, resource |
| content | JSONB | Type-specific payload |
| embedding | vector(384) | pgvector embedding (dimension per ADR-007) |
| model_version | TEXT | Embedding model that produced the vector |
| created_at | TIMESTAMPTZ | Record creation (system time) |
| valid_from | TIMESTAMPTZ | Business validity start (valid time) |
| valid_to | TIMESTAMPTZ | Business validity end (NULL = current) |
| version | INT | Optimistic concurrency version |
| status | ENUM | active, consolidated, archived |
| confidence | FLOAT | 0.0-1.0 confidence score |
| source_agent | TEXT | Agent that created the record |
| access_level | ENUM | public, agent_scoped, user_only, system, sensitive |
| metadata | JSONB | Extensible metadata |

## 3ngram-specific: bi-temporal versioning

Schemas MUST support bi-temporal queries (ADR-003, system design):

- **System time** (`created_at`): when the record was stored
- **Valid time** (`valid_from`, `valid_to`): when the fact was true
- UPDATE creates a new version; old version gets `valid_to` set
- Version chain integrity enforced by `expected_version` optimistic lock

## Format progression by phase

| Phase | Format | Use |
|-------|--------|-----|
| Design | Prose tables in markdown | Human review, design docs |
| Specification | JSON Schema / OpenAPI | Machine-validatable contracts |
| Implementation | SQL DDL + Pydantic models | Database + application layer |
| Runtime | Pydantic validation | Request/response enforcement |

Start with prose tables in design phase. Progress to formal schemas
as implementation approaches.

## Key tables (from system design)

| Table | Purpose | ADR Reference |
|-------|---------|---------------|
| memory_records | Core memory storage | ADR-003 |
| memory_versions | Bi-temporal version chain | ADR-003 |
| memory_edges | Knowledge graph relationships | ADR-009 |
| librarian_audit | Gate decision logging | ADR-012 |
| agent_registry | Agent identity and trust levels | ADR-002 |
| embeddings_metadata | Model version tracking | ADR-007 |

# Safety / Limits

- Read-only: do not create schema files without explicit user request.
- Do not invent fields not traceable to the system design or ADRs.
- Flag any schema change that would break bi-temporal versioning
  invariants.
- Data classification MUST be assigned before implementation (STD-044).
