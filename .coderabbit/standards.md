# CodeRabbit Standards — 3ngram

Mechanically-checkable rules for AI code review. These supplement
`path_instructions` in `.coderabbit.yaml`.

## Design-First (STD-020)

1. Implementation code in `src/engram/` (excluding stubs, Protocol
   definitions, `__init__.py` re-exports) MUST cite an approved
   technical spec document ID in the PR description.

## Architecture Decision Gates

1. ADR-003: No imports of Qdrant, Pinecone, ChromaDB, Milvus,
   Weaviate, or FAISS as primary store.
2. ADR-007: Embedding model names and dimensions MUST NOT be
   hardcoded outside `src/engram/embedding/`.
3. ADR-008: Agent roles MUST be defined as Python `Protocol` classes,
   not concrete class inheritance from a base agent.
4. ADR-009: No imports of Neo4j, py2neo, neomodel, or neo4j-driver.
   NetworkX is the current graph implementation.
5. ADR-012: Memory writes MUST pass through the Librarian Gate.
   Direct storage writes bypassing the gate are not permitted.

## Python Quality (STD-005)

1. All public functions and methods MUST have type annotations (mypy
   strict). No bare `# type: ignore` without a specific error code.
2. No bare `except:` or `except Exception: pass`. Module boundaries
   use aiobreaker + tenacity, not manual try/except chains.
3. No `time.sleep()`, synchronous `requests.get`, or blocking I/O in
   async contexts. Use `asyncio.sleep`, `aiohttp`, `asyncpg`.

## Security (STD-007)

1. No SQL string concatenation or f-string formatting for queries.
   All database queries MUST use parameterized queries.
2. No hardcoded secrets, tokens, API keys. Use `os.environ` or
   pydantic `BaseSettings`.

## Module Boundaries

1. Cross-module imports go through public interfaces in `__init__.py`.
   No imports of private symbols (`_name`) from other modules.
