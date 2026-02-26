---
paths:
  - "src/engram/auth/**/*.py"
  - "src/engram/gate/**/*.py"
---

# Auth & Gate Security

- Trust boundaries: all external input validated before reaching gate logic
- Token/credential handling: never log, never store plaintext, use secret manager
- Librarian Gate (ADR-012): declarative rules evaluated before RL advisor
- Gate decisions must be auditable — log decision path, not content
- Rate limiting at gate boundary, not inside core logic
- Fail closed: deny on error, never fail open
