# ADR 0001: Registry Storage

## Status

Accepted (Phase 1.5), 2026-05-22.

## Decision

Phase 2 should use SQLite as the primary persistent registry store.

The default registry boundary is one SQLite database per AAM workspace. The SQLite file is workspace-scoped and should live under workspace-local AAM metadata, for example `.aam/registry.sqlite3`. Phase 2 should not design a multi-workspace shared registry database.

Deterministic JSON remains the debug and interchange export format. It is not the primary registry store.

DuckDB is reserved as a future analytics and reporting option. It is not the primary Phase 2 registry store.

`UsageEvent`, `AuditLog`, and `RejectionEvent` placeholders may include `workspace_id` for future diagnostics, migration, and cross-workspace reporting, even though the Phase 2 registry database itself is workspace-scoped.

## Context

Phase 1 provides an `InMemoryRegistry` query projection built from manifest, files, validation output, content hashes, Asset Cards, and graph projection. Phase 2 needs persistence without changing the architectural rule that the manifest remains the source of truth and the registry remains rebuildable.

Phase 2 storage must support:

- deterministic rebuilds from manifest and asset content;
- local-first operation with no server requirement;
- queryable packages, assets, profiles, dependencies, reverse dependencies, Asset Cards, graph nodes/edges, and validation issues;
- future append-only usage, audit, and rejection placeholders;
- straightforward CLI and service integration;
- simple backup, deletion, and workspace portability.

Phase 1.5 is a technical spike checkpoint. It must not implement the production `RegistryStore`, production migrations, import workflow, HTTP API, MCP server, Web UI, assembly planning, package lock, materialization, or semantic search.

## Alternatives

### SQLite

SQLite is an embedded relational database included with Python through the standard library `sqlite3` module. It supports durable local storage, transactions, indexes, relational joins, views, and deterministic query ordering when explicitly specified.

Pros:

- No runtime service.
- No mandatory production dependency beyond Python standard library access.
- Good fit for local-first workspace data.
- Mature transaction and indexing behavior.
- Easy to inspect, back up, delete, and rebuild.
- Suitable for CLI, future local API, and future MCP-backed query workloads.

Cons:

- Schema migrations need deliberate versioning.
- JSON-heavy fields need clear serialization rules.
- Concurrent writers must remain controlled.
- Analytical workloads may need separate optimization later.

### Deterministic JSON as Primary Store

Deterministic JSON could serialize the entire registry projection to a file and reload it.

Pros:

- Human-readable.
- Easy to diff in tests.
- Natural fit for snapshot and interchange workflows.
- No database schema or migration machinery.

Cons:

- Weak incremental update story.
- Inefficient for filtered queries and relationship traversal as registry size grows.
- Harder to enforce relational integrity.
- Awkward for append-only events and future query service evolution.

Decision: keep deterministic JSON as debug/interchange export, not as the primary persistent registry store.

### DuckDB

DuckDB is an embedded analytical database with strong columnar analytics and SQL support.

Pros:

- Excellent analytical query performance.
- Good future fit for reporting, dashboard metrics, and registry analytics.
- Strong import/export capabilities.

Cons:

- Adds a runtime dependency.
- Optimized for analytics, not necessarily small transactional registry updates.
- Larger conceptual footprint than needed for Phase 2.
- Not required for the MVP query projection.

Decision: reserve DuckDB for future analytics/reporting. Do not make it the Phase 2 primary registry store.

## Rationale

SQLite matches AAM's local-first and private-first model while keeping Phase 2 small. It gives Phase 2 durable query projection storage without forcing a daemon, server, or cloud dependency. It also preserves the Phase 1 rule that registry data is a rebuildable projection from manifest and asset files, because the SQLite database can be dropped and rebuilt from package sources.

A workspace-scoped SQLite database keeps ownership and deletion simple. It avoids premature design for team mode or shared multi-workspace registries, which would introduce identity, migration, locking, and governance problems before the personal local workflow is stable.

Deterministic JSON remains valuable, but as an export surface. It should be generated with stable key ordering and deterministic list ordering so tests, debug snapshots, and future interchange workflows can compare registry state reproducibly.

DuckDB should stay out of the Phase 2 critical path. It is a plausible future companion for reporting and dashboard use cases, but using it as the primary registry store would add dependency and transaction complexity before AAM needs analytical scale.

## Consequences

Phase 2 implementation specs should define:

- a `RegistryStore` interface backed by SQLite;
- a schema version table;
- rebuild semantics from manifest and content;
- deterministic JSON export semantics;
- explicit transaction boundaries;
- table indexes for common query service access patterns;
- a migration strategy only as far as Phase 2 needs it.

Phase 2 should not:

- create one shared database across multiple workspaces;
- add DuckDB to production runtime dependencies for registry storage;
- treat deterministic JSON as the authoritative registry store;
- allow SQLite registry state to supersede manifest truth;
- let CLI code bypass services and query the database directly.

This ADR does not require a SQLite probe. The Phase 1 model shape maps directly to relational tables, and Python's standard `sqlite3` module is enough to validate feasibility during Phase 2 implementation.

## Non-goals

- No production persistent `RegistryStore` implementation in Phase 1.5.
- No production migration system in Phase 1.5.
- No local import workflow.
- No GitHub importer.
- No HTTP API or MCP server.
- No Web UI or graph visualization UI.
- No profile closure, assembly planning, package lock, or materialization.
- No spike-only dependency added to production runtime dependencies.
