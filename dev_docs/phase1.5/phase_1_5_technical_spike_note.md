# Phase 1.5 Technical Spike Note

## Status

Phase 1.5 Work Orders WO1-WO7 are complete and merged into `main`.

This note summarizes the technical spike decisions needed before Phase 2. It does not claim that Phase 2+ production capabilities have been implemented.

## Work Order Summary

| Work Order | Deliverables | Result |
| --- | --- | --- |
| WO1 — Phase 1 Handoff Audit | `phase_1_handoff_review.md` | Phase 1 accepted for Phase 1.5/Phase 2 planning. No P0/P1 handoff blockers. |
| WO2 — Registry Storage Spike and ADR | ADR 0001, `registry_schema_draft.md` | SQLite selected as primary registry store; deterministic JSON export retained; DuckDB deferred. |
| WO3 — Usage / Audit / Rejection Event Placeholder ADR | ADR 0002 | Append-only `UsageEvent`, `AuditLog`, and `RejectionEvent` placeholders defined. |
| WO4 — API and MCP Framework Spike | ADR 0003 | FastAPI selected for future Local Agent Gateway API; official MCP Python SDK selected for future MCP server; stdio first. |
| WO5 — Profile / Assembly / Lockfile Complexity Note | ADR 0004, complexity note | Phase 3 service boundaries defined; Phase 3 minimal explain/validate split from Phase 4A full API. |
| WO6 — Frontend and Graph Stack ADR | ADR 0005 | React + Vite + TypeScript selected for future Web Asset Browser; Cytoscape.js selected for relationship graph. |
| WO7 — CI, GitHub Templates, and Release Convention | CI, templates, ADR 0006 | CI now runs lint, tests, and installed CLI smoke; Work Order/PR templates and release/tag convention defined. |

## Accepted Decisions

### Registry Storage

- Primary Phase 2 registry store: SQLite.
- Registry boundary: one SQLite database per AAM workspace.
- Suggested path: `.aam/registry.sqlite3`.
- Do not design a multi-workspace shared registry database in Phase 2.
- Deterministic JSON is the debug/interchange export, not the primary store.
- DuckDB is a future analytics/reporting option only.
- `InMemoryRegistry` maps to relational package, asset, profile, asset card, dependency, graph, and validation tables.

Authoritative references:

- `dev_docs/phase1.5/adr_0001_registry_storage.md`
- `dev_docs/phase1.5/registry_schema_draft.md`

### Event Placeholders

- Reserve append-only `UsageEvent`, `AuditLog`, and `RejectionEvent` placeholders.
- Include `workspace_id` for future diagnostics and migration even though the registry database is workspace-scoped.
- Events are observations, not manifest truth or mutable workflow state.
- No recommendation learning, trust derivation, or governance workflow in Phase 2.

Authoritative reference:

- `dev_docs/phase1.5/adr_0002_usage_audit_rejection_events.md`

### API and MCP

- Future Phase 4A API framework: FastAPI.
- Future Phase 4B MCP framework: official MCP Python SDK.
- MCP transport priority: stdio first for the local AAM integration path.
- Streamable HTTP is a later transport option for production-style MCP deployment.
- API and MCP must remain adapters over AAM services.
- MCP must not implement registry, assembly, lockfile, or materialization business logic.

Authoritative reference:

- `dev_docs/phase1.5/adr_0003_api_and_mcp_framework.md`

### Composition, Assembly, and Lock

- Keep boundaries separate:
  - `ProfileClosureService`
  - `DiscoveryService`
  - `AssemblyPlanner`
  - `AssemblyPlanValidator`
  - approval boundary
  - `LockBuilder`
  - `MaterializationPreviewService`
- Phase 3 implements minimal deterministic reason-code explain/validate as service output.
- Phase 4A owns the fuller agent-facing explain/validate HTTP API.
- LockBuilder requires explicit approval input; valid does not mean approved.
- Package Lock records exact assets, versions, content hashes, source provenance, dependency graph, trust/permission snapshot, accepted warnings, policy snapshot, and materialization assumptions.

Authoritative references:

- `dev_docs/phase1.5/adr_0004_composition_assembly_lock_boundary.md`
- `dev_docs/phase1.5/profile_assembly_lock_complexity_note.md`

### Frontend and Graph

- Future Phase 6 frontend stack: React + Vite + TypeScript.
- Future Phase 7 relationship graph renderer: Cytoscape.js.
- React Flow is reserved for optional future explanatory/flow diagrams, not the primary relationship graph.
- Sigma.js and G6 remain future alternatives if concrete scale or feature blockers appear.
- No production Web UI or graph UI exists after Phase 1.5.

Authoritative reference:

- `dev_docs/phase1.5/adr_0005_frontend_and_graph_stack.md`

### CI and Release

- CI runs:
  - package installation with dev dependencies;
  - `ruff check .`;
  - `pytest`;
  - installed CLI smoke through `aam --help`.
- Work Order issues must include Goal, Scope, Deliverables, Acceptance Criteria, Non-goals, Test commands, and explicit warning against production Phase 2+ creep.
- PRs must record scope, validation, review, and non-goals.
- Work Order PRs use squash merge only.
- Phase 1.5 tag can only be created after WO9 is merged into `main` and final verification passes.

Authoritative reference:

- `dev_docs/phase1.5/adr_0006_ci_and_release_convention.md`

## Deferred Decisions

These are intentionally deferred and should not be reopened unless a concrete blocker appears:

- Exact SQLite migration command and schema version integer format.
- Full rebuild versus package-level rebuild implementation strategy.
- Whether graph tables are fully materialized or rebuilt on demand.
- Exact deterministic JSON export CLI command shape.
- Event id generation, retention/privacy policy, and complete SQL indexes.
- Phase 4A request/response schemas and local API security implementation details.
- Phase 4B MCP tool/resource/prompt inventory and SDK version pin.
- Phase 6 frontend package layout, component library, test runner, accessibility tooling, and Node version policy.
- Phase 7 Cytoscape.js React integration wrapper, layout strategy, and large-graph degraded mode.

## Phase 2 Technical Constraints

Phase 2 should implement persistent registry and related CLI/query usability within these constraints:

- Manifest remains the source of truth.
- Registry remains a rebuildable query projection.
- SQLite is workspace-scoped; no multi-workspace shared database.
- Deterministic JSON is export/debug only.
- CLI calls services; CLI does not query SQLite directly.
- No GitHub importer unless Phase 2 spec explicitly scopes a local import precursor separately.
- No production HTTP API.
- No production MCP server.
- No Web UI.
- No graph visualization UI.
- No profile closure execution.
- No assembly planning.
- No package lock generation.
- No materialization.
- No semantic search.
- Event placeholders must not implement recommendation learning.
- Any dependency additions must be justified by the Phase 2 implementation spec and kept out of spike-only paths.

## Recommended Phase 2 Implementation Spec Structure

1. Status, goal, scope, and non-goals.
2. Phase 1/1.5 inputs and authoritative references.
3. Workspace metadata layout.
4. SQLite registry store architecture.
5. Schema draft, schema versioning, and minimal migration policy.
6. `RegistryStore` interface and service boundary.
7. Rebuild flow from manifest to persistent projection.
8. Deterministic JSON export.
9. Query service integration and CLI adapter updates.
10. Event placeholder reservation, if included.
11. Validation and error handling behavior.
12. Fixtures and snapshot tests.
13. CLI smoke and user-facing docs updates.
14. Explicit non-goals and phase gates.
15. Work Orders with acceptance criteria.

## Unresolved P2/P3 Items for Planning

These are not Phase 1.5 blockers, but they should inform Phase 2/3/4 specs:

- Registry schema: decide whether `registry_meta` remains key-value or a dedicated schema version table is introduced.
- Registry schema: document absolute path fields as rebuild-time artifacts, not portable/export comparison keys.
- Registry schema: decide foreign key policy for validation issues and dependency tables.
- Registry schema: define consistency rules for denormalized Asset Card scalar columns versus `card_json`.
- Registry schema: clarify declared dependency references versus resolved dependency edges.
- Events: decide whether event records need both `occurred_at` and `recorded_at`.
- Events: decide unified export discriminator fields and cross-event correlation conventions.
- API/MCP: record SDK/framework versions at implementation time.
- API/MCP: review MCP transport/security recommendations again when Phase 4B starts.
- Composition docs: avoid drift between ADR 0004 and the complexity note when turning them into Phase 3 implementation specs.
- Frontend: decide Node/Vite version constraints in Phase 6.
- CI/templates: issue template defaults are generic; phase-specific labels still need to be applied at issue creation.

## Final Note

Phase 1.5 froze key technical directions without implementing production Phase 2+ capabilities. Phase 2 can now start from a concrete SQLite registry plan, explicit workspace boundary, deterministic export policy, event placeholder shape, and established GitHub/CI workflow.
