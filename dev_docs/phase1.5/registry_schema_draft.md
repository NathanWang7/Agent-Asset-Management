# Registry Schema Draft

## Purpose

This draft maps the Phase 1 `InMemoryRegistry` projection to a Phase 2 SQLite-backed `RegistryStore`. It is a planning artifact, not a production migration or implementation.

The manifest remains the source of truth. The SQLite registry is a workspace-local query projection that can be deleted and rebuilt from package manifests, asset files, validation output, content hashes, Asset Cards, and graph projection.

## Storage Boundary

- Primary store: SQLite.
- Workspace boundary: one SQLite database per AAM workspace.
- Suggested path: `.aam/registry.sqlite3` under the workspace root.
- No multi-workspace shared registry database in Phase 2.
- Deterministic JSON export should be generated from the store or in-memory projection for debug/interchange.
- `workspace_id` may appear in event placeholders for future diagnostics and migration, but the registry database itself remains workspace-scoped.

## InMemoryRegistry Mapping

| Phase 1 projection | Phase 2 table or view |
| --- | --- |
| `InMemoryRegistry.packages` | `registry_packages` |
| `InMemoryRegistry.assets` | `registry_assets` |
| `InMemoryRegistry.profiles` | `registry_profiles` |
| `InMemoryRegistry.asset_cards` | `registry_asset_cards` |
| `InMemoryRegistry.dependencies` | `registry_asset_dependencies` |
| `InMemoryRegistry.reverse_dependencies` | derived query or view over `registry_asset_dependencies` |
| `InMemoryRegistry.graph.nodes` | `registry_graph_nodes` |
| `InMemoryRegistry.graph.edges` | `registry_graph_edges` |
| `InMemoryRegistry.validation_report` | `registry_validation_issues` plus package-level build status |

## Draft Tables

Types below are logical. Phase 2 should translate Python enums to stable text values and serialize structured fields as deterministic JSON text where the field is not worth normalizing yet.

### `registry_meta`

Stores registry-level metadata.

| Column | Type | Notes |
| --- | --- | --- |
| `key` | `TEXT PRIMARY KEY` | Example: `schema_version`, `created_at`, `updated_at`. |
| `value` | `TEXT NOT NULL` | Deterministic scalar text value. |

Required keys:

- `schema_version`
- `workspace_root`
- `created_at`
- `updated_at`

### `registry_packages`

Stores indexed package projections.

| Column | Type | Notes |
| --- | --- | --- |
| `package_id` | `TEXT PRIMARY KEY` | Manifest package id. |
| `name` | `TEXT NOT NULL` | Manifest package name. |
| `version` | `TEXT NOT NULL` | Manifest package version. |
| `indexed_at` | `TEXT NOT NULL` | UTC ISO-8601 timestamp. |
| `description` | `TEXT` | Nullable. |
| `tags_json` | `TEXT NOT NULL` | Deterministic JSON list. |
| `source_kind` | `TEXT NOT NULL` | Source enum value. |
| `source_original_location` | `TEXT` | Nullable. |
| `source_resolved_ref` | `TEXT` | Nullable. |

Indexes:

- `idx_registry_packages_version` on `version`
- `idx_registry_packages_source_kind` on `source_kind`

### `registry_assets`

Stores indexed asset projections.

| Column | Type | Notes |
| --- | --- | --- |
| `qualified_id` | `TEXT PRIMARY KEY` | `package_id:asset_id@package_version`. |
| `package_id` | `TEXT NOT NULL` | References `registry_packages(package_id)`. |
| `package_version` | `TEXT NOT NULL` | Denormalized for query and rebuild checks. |
| `asset_id` | `TEXT NOT NULL` | Manifest asset id. |
| `indexed_at` | `TEXT NOT NULL` | UTC ISO-8601 timestamp. |
| `type` | `TEXT NOT NULL` | Asset type enum value. |
| `path` | `TEXT NOT NULL` | Manifest-relative path. |
| `absolute_path` | `TEXT NOT NULL` | Resolved path at index time. |
| `visibility` | `TEXT NOT NULL` | Visibility enum value. |
| `lifecycle_status` | `TEXT NOT NULL` | Lifecycle enum value. |
| `trust_status` | `TEXT NOT NULL` | Trust enum value. |
| `description` | `TEXT` | Nullable. |
| `tags_json` | `TEXT NOT NULL` | Deterministic JSON list. |
| `depends_on_json` | `TEXT NOT NULL` | Original manifest references. |
| `target_hosts_json` | `TEXT NOT NULL` | Deterministic JSON list. |
| `permissions_json` | `TEXT NOT NULL` | Deterministic JSON object. |
| `context_cost_json` | `TEXT NOT NULL` | Deterministic JSON object. |
| `content_hash` | `TEXT NOT NULL` | Hash from asset file content. |
| `source_kind` | `TEXT NOT NULL` | Package source in Phase 2. |
| `source_original_location` | `TEXT` | Nullable. |
| `source_resolved_ref` | `TEXT` | Nullable. |

Constraints:

- Unique `(package_id, package_version, asset_id)`.
- Foreign key from `package_id` to `registry_packages(package_id)`.

Indexes:

- `idx_registry_assets_package` on `package_id`
- `idx_registry_assets_type` on `type`
- `idx_registry_assets_trust` on `trust_status`
- `idx_registry_assets_lifecycle` on `lifecycle_status`
- `idx_registry_assets_hash` on `content_hash`

### `registry_profiles`

Stores indexed profile projections.

| Column | Type | Notes |
| --- | --- | --- |
| `qualified_id` | `TEXT PRIMARY KEY` | `package_id:profile_id@package_version`. |
| `package_id` | `TEXT NOT NULL` | References `registry_packages(package_id)`. |
| `package_version` | `TEXT NOT NULL` | Denormalized for query and rebuild checks. |
| `profile_id` | `TEXT NOT NULL` | Manifest profile id. |
| `indexed_at` | `TEXT NOT NULL` | UTC ISO-8601 timestamp. |
| `target_host` | `TEXT NOT NULL` | Profile target host. |
| `description` | `TEXT` | Nullable. |
| `includes_json` | `TEXT NOT NULL` | Original manifest include references. |
| `resolved_includes_json` | `TEXT NOT NULL` | Deterministic JSON list of qualified asset ids. |
| `tags_json` | `TEXT NOT NULL` | Deterministic JSON list. |

Constraints:

- Unique `(package_id, package_version, profile_id)`.
- Foreign key from `package_id` to `registry_packages(package_id)`.

Indexes:

- `idx_registry_profiles_package` on `package_id`
- `idx_registry_profiles_target_host` on `target_host`

### `registry_asset_cards`

Stores deterministic Asset Card projections.

| Column | Type | Notes |
| --- | --- | --- |
| `asset_qualified_id` | `TEXT PRIMARY KEY` | References `registry_assets(qualified_id)`. |
| `card_json` | `TEXT NOT NULL` | Full deterministic Asset Card JSON. |
| `title` | `TEXT NOT NULL` | Duplicated for quick display. |
| `summary` | `TEXT` | Nullable. |
| `risk_level` | `TEXT NOT NULL` | Risk enum value. |
| `estimated_context_cost` | `INTEGER` | Nullable. |
| `content_hash` | `TEXT NOT NULL` | Duplicated consistency check. |

Indexes:

- `idx_registry_asset_cards_risk` on `risk_level`

### `registry_asset_dependencies`

Stores resolved asset dependency edges.

| Column | Type | Notes |
| --- | --- | --- |
| `asset_qualified_id` | `TEXT NOT NULL` | Dependent asset. |
| `dependency_qualified_id` | `TEXT NOT NULL` | Required asset. |
| `position` | `INTEGER NOT NULL` | Original deterministic order. |

Primary key:

- `(asset_qualified_id, dependency_qualified_id)`

Indexes:

- `idx_registry_asset_dependencies_asset` on `asset_qualified_id`
- `idx_registry_asset_dependencies_dependency` on `dependency_qualified_id`

Reverse dependencies should be served by a query or view:

```sql
SELECT asset_qualified_id
FROM registry_asset_dependencies
WHERE dependency_qualified_id = ?
ORDER BY asset_qualified_id;
```

A Phase 2 implementation may expose the same lookup as a named view:

```sql
CREATE VIEW registry_reverse_asset_dependencies AS
SELECT
  dependency_qualified_id,
  asset_qualified_id
FROM registry_asset_dependencies;
```

### `registry_profile_includes`

Stores resolved profile-to-asset include edges. This table is not a direct Phase 1 `InMemoryRegistry` field, but it avoids repeatedly parsing `resolved_includes_json`.

| Column | Type | Notes |
| --- | --- | --- |
| `profile_qualified_id` | `TEXT NOT NULL` | Profile projection id. |
| `asset_qualified_id` | `TEXT NOT NULL` | Included asset projection id. |
| `position` | `INTEGER NOT NULL` | Original deterministic order. |

Primary key:

- `(profile_qualified_id, asset_qualified_id)`

Indexes:

- `idx_registry_profile_includes_profile` on `profile_qualified_id`
- `idx_registry_profile_includes_asset` on `asset_qualified_id`

### `registry_graph_nodes`

Stores lightweight graph projection nodes.

| Column | Type | Notes |
| --- | --- | --- |
| `node_id` | `TEXT PRIMARY KEY` | Graph node id. |
| `type` | `TEXT NOT NULL` | Graph node type enum value. |
| `label` | `TEXT NOT NULL` | Display label. |
| `metadata_json` | `TEXT NOT NULL` | Deterministic JSON object. |

Indexes:

- `idx_registry_graph_nodes_type` on `type`

### `registry_graph_edges`

Stores lightweight graph projection edges.

| Column | Type | Notes |
| --- | --- | --- |
| `edge_id` | `TEXT PRIMARY KEY` | Deterministic edge id. |
| `type` | `TEXT NOT NULL` | Graph edge type enum value. |
| `source_node_id` | `TEXT NOT NULL` | Source graph node id. |
| `target_node_id` | `TEXT NOT NULL` | Target graph node id. |
| `metadata_json` | `TEXT NOT NULL` | Deterministic JSON object. |

Indexes:

- `idx_registry_graph_edges_type` on `type`
- `idx_registry_graph_edges_source` on `source_node_id`
- `idx_registry_graph_edges_target` on `target_node_id`

### `registry_validation_issues`

Stores validation report issues from the registry build.

| Column | Type | Notes |
| --- | --- | --- |
| `issue_id` | `TEXT PRIMARY KEY` | Deterministic id from severity, code, path, and message hash. |
| `package_id` | `TEXT NOT NULL` | Package under validation. |
| `severity` | `TEXT NOT NULL` | Validation severity enum value. |
| `code` | `TEXT NOT NULL` | Stable validation code. |
| `message` | `TEXT NOT NULL` | Human-readable message. |
| `path` | `TEXT` | Nullable related manifest/file path. |
| `metadata_json` | `TEXT NOT NULL` | Deterministic JSON object for future detail. |

Indexes:

- `idx_registry_validation_package` on `package_id`
- `idx_registry_validation_severity` on `severity`
- `idx_registry_validation_code` on `code`

## Reserved Event Placeholder Tables

Phase 2 may reserve append-only placeholders, but detailed event semantics belong to ADR 0002. The table names below are included only to show that the SQLite registry schema has reserved space for those future placeholders.

Column-level definitions, constraints, indexes, and retention rules are intentionally deferred to WO3 / ADR 0002 so WO2 does not preempt the event-shape decision.

### `registry_usage_events`

Reserved for future `UsageEvent` records. Include `workspace_id`, `event_id`, `occurred_at`, actor fields, asset/package references, action, result, reason codes, and metadata JSON.

### `registry_audit_log`

Reserved for future `AuditLog` records. Include `workspace_id`, `audit_id`, `occurred_at`, actor fields, operation, target references, decision/result, policy snapshot reference, and metadata JSON.

### `registry_rejection_events`

Reserved for future `RejectionEvent` records. Include `workspace_id`, `rejection_id`, `occurred_at`, actor fields, rejected target, rejection reason code, freeform note, follow-up action, and metadata JSON.

## Deterministic JSON Rules

Phase 2 should use one serialization policy for JSON stored in SQLite and JSON exported for debug/interchange:

- sort object keys;
- preserve deterministic list order from manifest or projection builders;
- use UTF-8;
- avoid volatile fields unless explicitly part of the projection;
- serialize enum values as strings;
- represent timestamps as UTC ISO-8601 strings;
- include schema/export version metadata in exported files.

## Rebuild Semantics

The Phase 2 `RegistryStore` should support a full workspace rebuild:

1. Parse manifest files through existing parser services.
2. Validate packages through validator services.
3. Build indexed models and projections through registry builder services.
4. Open a SQLite transaction.
5. Replace rows for rebuilt packages and related projections.
6. Commit only when the full package projection is internally consistent.
7. Roll back on validation or write errors.

CLI commands must continue to call services, not duplicate parser, validator, index, or database query logic.

## Phase 2 Open Details

These are implementation-spec details, not blockers for this ADR:

- exact `.aam/` workspace metadata layout;
- schema version integer format;
- full rebuild versus package-level rebuild first;
- whether graph tables are fully materialized or rebuilt on demand;
- exact deterministic JSON export command shape;
- migration command naming and user-facing error messages.

## Non-goals

- No production `RegistryStore` implementation.
- No production migration system.
- No local import workflow.
- No GitHub importer.
- No production HTTP API or MCP server.
- No Web UI or graph visualization UI.
- No profile closure, assembly planning, lockfile generation, or materialization.
