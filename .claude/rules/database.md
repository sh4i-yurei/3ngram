---
paths:
  - "src/engram/storage/**/*.py"
  - "src/engram/models/**/*.py"
---

# Storage & Models

- Postgres+pgvector (ADR-003): all vector ops via pgvector, no separate vector DB
- Parameterized queries only — NEVER string concatenation for SQL
- Migrations: alembic, one migration per schema change, always reversible
- Connection pooling via asyncpg, not per-request connections
- Models use SQLAlchemy 2.0 mapped_column style
- Embedding adapter pattern (ADR-007): swappable interface, never call embedding model directly
