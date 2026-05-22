# Phase 1.5 Technical Spike Checkpoint Implementation Spec

## 1. Status

Draft v0.2

This document is the Phase 1.5 implementation spec for Agent Asset Management.

Phase 1.5 is a technical spike checkpoint between Phase 1 and Phase 2. It is not a feature-building phase. Its purpose is to make the technical decisions that Phase 2 through Phase 7 will depend on, using the actual Phase 1 implementation as input.

Phase 1 established the local package system foundation:

```text
package.yaml
  -> typed manifest models
  -> parser
  -> validator
  -> content hash
  -> Asset Card projection
  -> in-memory registry
  -> graph projection
  -> CLI query/demo
```

Phase 1.5 should answer the technical questions that should not be left to Phase 2 implementation time:

1. Which registry persistence backend should be used?
2. How should `InMemoryRegistry` map into a future `RegistryStore`?
3. What are the minimal persistent shapes for `UsageEvent`, `AuditLog`, and `RejectionEvent`?
4. Which API framework should back the future local Agent Gateway API?
5. Which MCP framework / SDK should back the future MCP Server?
6. Are the Profile closure, Assembly Plan, profile delta, and Package Lock model boundaries clear enough for Phase 3?
7. Which frontend stack should Phase 6 use?
8. Which graph visualization stack should Phase 7 use?
9. Are CI, PR, issue, milestone, and release/tag conventions stable enough for Phase 2+?

## 2. Goal

The goal of Phase 1.5 is to produce decision records, lightweight probes, and engineering conventions that let Phase 2 start without re-litigating storage, API, MCP, frontend, graph, CI, or release strategy.

Phase 1.5 should produce:

1. A Phase 1 handoff audit note.
2. A registry storage ADR.
3. A registry schema draft showing how Phase 1 `InMemoryRegistry` maps to persistent storage.
4. A UsageEvent / AuditLog / RejectionEvent placeholder ADR.
5. An API + MCP framework ADR.
6. Minimal FastAPI and MCP probes.
7. A Profile closure / Assembly / Lockfile complexity note.
8. A frontend + graph stack ADR.
9. Minimal React + Vite and graph rendering probes, if lightweight.
10. CI baseline and GitHub issue/PR templates, if missing or incomplete.
11. Release/tag convention for phase checkpoints.
12. A final dual AI review gate using Codex and Claude Code before phase closeout.

The most important output is not running code. The most important output is that Phase 2 can proceed with a stable technical direction.

## 3. Phase 1.5 Decisions

Unless a spike produces strong contrary evidence, Phase 1.5 should adopt the following decisions.

### 3.1 Registry Storage Decision

Use SQLite as the primary local registry persistence backend.

Recommended decision:

```text
Primary registry store: SQLite
Debug/interchange export: deterministic JSON
Future analytics/reporting enhancement: DuckDB optional, not primary registry store
```

Rationale:

- AAM is local-first and private-first.
- The registry is a query projection, not the manifest source of truth.
- Phase 2 needs transactional local persistence for packages, assets, profiles, cards, dependencies, graph edges, import runs, usage events, audit logs, and rejection events.
- SQLite fits embedded local transactional registry storage better than a JSON file.
- JSON remains useful for deterministic graph and registry exports.
- DuckDB remains useful later for analytic/reporting workloads, but should not be the primary registry store in Phase 2.

### 3.2 RegistryStore Mapping Decision

Phase 2 should map Phase 1 `InMemoryRegistry` into a `RegistryStore` boundary rather than letting each caller write SQL directly.

Draft mapping:

```text
InMemoryRegistry.packages              -> registry_packages
InMemoryRegistry.assets                -> registry_assets
InMemoryRegistry.profiles              -> registry_profiles
InMemoryRegistry.asset_cards           -> registry_asset_cards
InMemoryRegistry.dependencies          -> registry_asset_dependencies
InMemoryRegistry.reverse_dependencies  -> derived query / view
InMemoryRegistry.graph.nodes           -> registry_graph_nodes
InMemoryRegistry.graph.edges           -> registry_graph_edges
InMemoryRegistry.validation_report     -> registry_validation_issues
```

Phase 2 should introduce:

```text
RegistryStore
RegistryWriter
RegistryReader
RegistryRebuilder
RegistryService
AssetQueryService
GraphQueryService
StatsService
```

But Phase 1.5 should not implement the production store.

### 3.3 Usage / Audit / Rejection Event Decision

Phase 2 should reserve append-only persistence for usage, audit, and rejection signals.

Minimal model direction:

```text
UsageEvent:
  id
  event_type
  occurred_at
  client_name
  actor
  workspace_id
  package_id
  asset_id
  profile_id
  assembly_plan_id
  payload_json

AuditLog:
  id
  occurred_at
  actor
  action
  target_type
  target_id
  decision
  reason_code
  payload_json

RejectionEvent:
  id
  occurred_at
  rejected_target_type
  rejected_target_id
  asset_id
  assembly_plan_id
  reason_code
  user_action
  context_json
```

Phase 2 only needs placeholder persistence. It should not implement recommendation learning.

`RejectionEvent.user_action` should reserve at least:

```text
ignore_once
review_now
block_asset
```

Future values may include:

```text
mark_trusted
mark_sandbox_only
deprecate_asset
suppress_for_context
```

### 3.4 API Framework Decision

Use FastAPI for the future local Agent Gateway API.

Recommended decision:

```text
API framework: FastAPI
API contract style: typed Pydantic response models + OpenAPI schema
Phase 4A server mode: localhost/local-only by default
```

Rationale:

- Phase 4A requires OpenAPI schema and stable response models.
- Current Phase 1 models are already typed.
- The API is a local service contract for Web UI, MCP wrapping, smoke tests, and local automation.
- A heavyweight backend framework is not necessary yet.

### 3.5 MCP Framework Decision

Use the official Model Context Protocol Python SDK for the future MCP server.

Recommended decision:

```text
MCP framework: official MCP Python SDK
Transport priority: stdio first
Future transport: localhost HTTP/SSE/streamable HTTP only if needed
Default mode: read-only + propose-only
```

MCP must wrap service boundaries. It must not independently implement registry query, assembly logic, or policy gates.

### 3.6 Frontend Stack Decision

Use React + Vite + TypeScript for the Phase 6 Web Asset Browser.

Recommended decision:

```text
Frontend framework: React
Build tooling: Vite
Language: TypeScript
Routing: lightweight client-side routing
API access: typed client generated or hand-written from OpenAPI
```

Do not use Next.js for the MVP unless a later phase introduces a strong need for SSR, server components, or production web deployment semantics.

### 3.7 Graph Visualization Decision

Use Cytoscape.js as the primary graph visualization library for Phase 7.

Recommended decision:

```text
Primary graph visualization: Cytoscape.js
Optional future flow/plan renderer: React Flow
```

Rationale:

- AAM relationship graph is graph-data-first: assets, packages, profiles, tags, targets, sources, locks, materialization runs, and edges.
- Cytoscape.js is better aligned with graph/network visualization and filtering.
- React Flow is useful for node-based workflow editors or explanatory diagrams, but should not be the default global relationship graph engine.

### 3.8 Profile / Assembly / Lockfile Boundary Decision

Phase 3 should implement the first production composition layer, but Phase 1.5 should only write a complexity note.

Recommended service boundaries:

```text
ProfileClosureService:
  input: profile_id, registry/query service, constraints
  output: ordered asset closure, dependency closure, warnings, missing refs

DiscoveryService:
  input: DiscoveryRequest
  output: candidate assets with scores and reason codes

AssemblyPlanner:
  input: DiscoveryRequest, optional base_profile
  output: AssemblyPlan with selected/excluded/profile_delta/warnings/rationale

AssemblyPlanValidator:
  input: AssemblyPlan
  output: validation result with policy issues and missing dependencies

LockBuilder:
  input: approved AssemblyPlan or ProfileClosure
  output: PackageLock snapshot

MaterializationPreviewService:
  input: PackageLock or closure
  output: preview tree/diff/report
```

Phase 3 should implement minimal explain/validate via reason codes and warnings. Fuller HTTP explain/validate API belongs to Phase 4A.

## 4. Scope

Phase 1.5 includes:

1. Auditing Phase 1 outputs against Phase 1 handoff expectations.
2. Writing ADRs for storage, events, API/MCP, composition boundaries, frontend/graph, CI/release conventions.
3. Creating lightweight spike/probe code only where needed to de-risk the decision.
4. Creating or updating GitHub milestone, issues, labels, PR template, issue template, and CI baseline.
5. Creating a final `docs/phase1_5_technical_spike_note.md` summarizing decisions and implications for Phase 2.
6. Running a final dual AI review gate against the development docs before phase closeout.

## 5. Non-goals

Phase 1.5 must not implement production Phase 2+ capabilities.

Do not implement:

1. Production `RegistryStore`.
2. Production SQLite migration system.
3. Local import workflow.
4. GitHub importer.
5. ImportRun production persistence.
6. Production FastAPI server.
7. Production MCP server.
8. Production Profile closure service.
9. Production Assembly Planner.
10. Production Package Lock model.
11. Production materialization preview.
12. Web UI.
13. Graph UI.
14. Asset editing.
15. Full rejection-to-governance UI.
16. Semantic search.
17. Team workspace.
18. Any Agent runtime behavior.

Spike code must stay under `spikes/phase1_5/` or equivalent clearly non-production paths unless the work order is specifically about CI/templates/docs.

## 6. Affected Modules

Phase 1.5 may touch:

```text
docs/
docs/adr/
docs/review/
spikes/phase1_5/
.github/workflows/
.github/ISSUE_TEMPLATE/
.github/pull_request_template.md
pyproject.toml only if needed for dev-only spike dependencies
```

Phase 1.5 should avoid touching production source unless a small correction is required to complete the Phase 1 handoff audit.

If a Phase 1 defect is found, fix it in the smallest possible PR and label it clearly as a Phase 1 handoff fix.

## 7. Data Models

Phase 1.5 should draft but not production-implement the following models.

### 7.1 Registry Store Tables Draft

```text
registry_packages
registry_assets
registry_profiles
registry_asset_cards
registry_asset_dependencies
registry_graph_nodes
registry_graph_edges
registry_validation_issues
registry_builds
```

### 7.2 Event Tables Draft

```text
usage_events
audit_logs
rejection_events
```

### 7.3 Composition Models Draft

```text
ProfileClosure
DiscoveryRequest
CandidateAsset
AssemblyPlan
AssemblyPlanAssetSelection
ProfileDelta
PackageLock
PolicySnapshot
MaterializationPreview
```

The final field-level definitions belong to Phase 2 or Phase 3 specs. Phase 1.5 should only define enough to prevent model-boundary ambiguity.

## 8. Public Interfaces

Phase 1.5 should propose the future public service interfaces but not implement them.

### 8.1 Future Registry Store Boundary

```python
class RegistryStore:
    def rebuild_from_registry(self, registry: InMemoryRegistry) -> RegistryBuildResult: ...
    def get_package(self, package_id: str) -> RegistryPackageRecord: ...
    def list_assets(self, filters: AssetQueryFilters | None = None) -> list[RegistryAssetRecord]: ...
    def get_asset(self, qualified_or_local_id: str) -> RegistryAssetRecord: ...
    def get_asset_card(self, qualified_or_local_id: str) -> AssetCardProjection: ...
    def get_dependencies(self, qualified_or_local_id: str) -> list[RegistryAssetRecord]: ...
    def get_reverse_dependencies(self, qualified_or_local_id: str) -> list[RegistryAssetRecord]: ...
    def export_graph(self, filters: GraphFilters | None = None) -> GraphProjection: ...
```

### 8.2 Future API Boundary

```text
GET  /v1/assets
GET  /v1/assets/{asset_id}
GET  /v1/assets/{asset_id}/card
GET  /v1/assets/{asset_id}/dependencies
GET  /v1/profiles/{profile_id}/closure
POST /v1/discover
POST /v1/assemble
POST /v1/assembly-plans/{plan_id}/validate
POST /v1/assembly-plans/{plan_id}/lock
POST /v1/materialize/preview
GET  /v1/stats
GET  /v1/graph
```

### 8.3 Future MCP Tool Boundary

```text
list_assets
search_assets
get_asset_card
get_asset_dependencies
propose_assembly_plan
explain_assembly_plan
validate_assembly_plan
```

MCP tools must default to read-only + propose-only.

## 9. Work Orders

Phase 1.5 should be completed through sequential work orders.

### WO1 — Phase 1 Handoff Audit

Goal:

Verify that Phase 1 is actually ready to support Phase 1.5 and Phase 2.

Tasks:

1. Review Phase 1 implementation against Phase 1 acceptance.
2. Confirm indexed timestamp exists where required.
3. Confirm registry contains content hash, Asset Card projection, dependencies, reverse dependencies, source provenance, trust, lifecycle, permissions, and graph projection.
4. Confirm CLI uses service boundaries rather than duplicating parser/index logic.
5. Confirm required fixtures exist.
6. Confirm tests and CLI smoke flow pass.
7. Write `docs/phase1_handoff_review.md`.

Deliverables:

```text
docs/phase1_handoff_review.md
```

Acceptance Criteria:

1. Handoff note clearly lists pass/fail status.
2. Any critical Phase 1 defect is either fixed or explicitly recorded as a blocker.
3. No Phase 2+ capability is implemented.

### WO2 — Registry Storage Spike and ADR

Goal:

Choose the registry persistence backend and draft the `InMemoryRegistry -> RegistryStore` mapping.

Tasks:

1. Write `docs/adr/0001-registry-storage.md`.
2. Create a lightweight SQLite probe under `spikes/phase1_5/sqlite_registry_probe.py` if helpful.
3. Draft table mapping in `docs/phase1_5_registry_schema_draft.md`.
4. Compare SQLite, JSON, and DuckDB.
5. Recommend SQLite as primary, JSON as deterministic export, DuckDB as future analytics option unless probe evidence contradicts this.

Deliverables:

```text
docs/adr/0001-registry-storage.md
docs/phase1_5_registry_schema_draft.md
spikes/phase1_5/sqlite_registry_probe.py optional
```

Acceptance Criteria:

1. Storage decision is explicit.
2. Phase 2 can implement RegistryStore from the draft without choosing a backend again.
3. Spike code is non-production and clearly isolated.
4. No production persistent registry is implemented.

### WO3 — Usage / Audit / Rejection Event Placeholder ADR

Goal:

Define the minimal append-only event persistence shapes Phase 2 should reserve.

Tasks:

1. Write `docs/adr/0002-usage-audit-rejection-events.md`.
2. Define minimal fields for `UsageEvent`, `AuditLog`, and `RejectionEvent`.
3. Define minimal rejection actions: `ignore_once`, `review_now`, `block_asset`.
4. State that Phase 2 only reserves/writes limited events and does not implement recommendation learning.
5. Explain how this supports Phase 6 minimal rejection handling and future governance.

Deliverables:

```text
docs/adr/0002-usage-audit-rejection-events.md
```

Acceptance Criteria:

1. Event models are append-only.
2. Event models do not become a complex analytics system.
3. Rejection-to-governance placeholder is aligned with future Review now / Ignore once / Block asset flow.

### WO4 — API and MCP Framework Spike

Goal:

Choose API and MCP frameworks and verify minimal feasibility.

Tasks:

1. Write `docs/adr/0003-api-and-mcp-framework.md`.
2. Create a minimal FastAPI probe under `spikes/phase1_5/fastapi_probe/`.
3. Create a minimal MCP Python SDK probe under `spikes/phase1_5/mcp_probe/`.
4. Show how future endpoints/tools wrap RegistryService / AssemblyService rather than implementing logic directly.
5. Document error/degraded-mode response expectations.
6. Do not add a production API or MCP server.

Deliverables:

```text
docs/adr/0003-api-and-mcp-framework.md
spikes/phase1_5/fastapi_probe/
spikes/phase1_5/mcp_probe/
```

Acceptance Criteria:

1. FastAPI is selected for Phase 4A unless probe fails.
2. Official MCP Python SDK is selected for Phase 4B unless probe fails.
3. Probes are isolated and do not affect package runtime.
4. Future gateway error/degraded-mode semantics are documented.

### WO5 — Profile / Assembly / Lockfile Complexity Note

Goal:

Clarify the model and service boundaries for Phase 3 before production implementation.

Tasks:

1. Write `docs/phase1_5_profile_assembly_lock_complexity_note.md`.
2. Write `docs/adr/0004-composition-assembly-lock-boundary.md`.
3. Define the roles of `ProfileClosureService`, `DiscoveryService`, `AssemblyPlanner`, `AssemblyPlanValidator`, `LockBuilder`, and `MaterializationPreviewService`.
4. Define minimal Phase 3 model expectations.
5. Separate Phase 3 minimal reason-code explain/validate from Phase 4A full API explain/validate.
6. Do not implement production composition services.

Deliverables:

```text
docs/phase1_5_profile_assembly_lock_complexity_note.md
docs/adr/0004-composition-assembly-lock-boundary.md
```

Acceptance Criteria:

1. Phase 3 can be scoped without ambiguity.
2. Assembly Plan is not confused with Package Lock.
3. Profile remains a baseline; Assembly Plan remains task-specific.
4. Package Lock remains the reproducibility boundary.
5. No production Phase 3 implementation is introduced.

### WO6 — Frontend and Graph Stack ADR

Goal:

Choose frontend and graph visualization stacks for Phase 6/7.

Tasks:

1. Write `docs/adr/0005-frontend-and-graph-stack.md`.
2. Recommend React + Vite + TypeScript for Phase 6.
3. Explain why Next.js is not needed for the MVP local asset browser.
4. Recommend Cytoscape.js for Phase 7 relationship graph.
5. Mention React Flow only as an optional future renderer for flow-like explanation diagrams.
6. Optionally add isolated probes under `spikes/phase1_5/react_vite_probe/` and `spikes/phase1_5/cytoscape_probe/`.

Deliverables:

```text
docs/adr/0005-frontend-and-graph-stack.md
spikes/phase1_5/react_vite_probe/ optional
spikes/phase1_5/cytoscape_probe/ optional
```

Acceptance Criteria:

1. Frontend stack is selected.
2. Graph stack is selected.
3. Phase 6 and Phase 7 no longer need to choose their primary UI technologies.
4. No production Web UI or Graph UI is introduced.

### WO7 — CI, GitHub Templates, and Release Convention

Goal:

Stabilize the GitHub-driven development workflow for Phase 2+.

Tasks:

1. Ensure CI exists and runs pytest.
2. Ensure ruff runs in CI if configured.
3. Add or update `.github/pull_request_template.md`.
4. Add or update `.github/ISSUE_TEMPLATE/work_order.md`.
5. Write `docs/adr/0006-ci-and-release-convention.md`.
6. Define phase tag naming.
7. Define semver convention if used.
8. Define that work orders are implemented through scoped PRs.

Deliverables:

```text
.github/workflows/ci.yml
.github/pull_request_template.md
.github/ISSUE_TEMPLATE/work_order.md
docs/adr/0006-ci-and-release-convention.md
```

Acceptance Criteria:

1. CI baseline is stable.
2. Work order issue template exists.
3. PR template enforces scope, tests, and review checklist.
4. Release/tag convention is explicit.
5. No unrelated production functionality is added.

### WO8 — Final Phase 1.5 Technical Spike Note

Goal:

Summarize all decisions and hand off to Phase 2.

Tasks:

1. Write `docs/phase1_5_technical_spike_note.md`.
2. Summarize decisions from ADR 0001-0006.
3. Summarize any spike results.
4. List Phase 2 implications.
5. List risks carried forward.
6. Define Phase 2 readiness checklist.
7. Optionally create `docs/phase2_preparation_notes.md`.

Deliverables:

```text
docs/phase1_5_technical_spike_note.md
docs/phase2_preparation_notes.md optional
```

Acceptance Criteria:

1. Phase 1.5 decisions are summarized in one place.
2. Phase 2 implementation spec can start from this note.
3. No open Phase 1.5 decision blocks Phase 2.

### WO9 — Final Dual AI Review and Phase Closeout

Goal:

Close Phase 1.5 only after both Codex and Claude Code have independently reviewed the completed phase against the development docs.

This work order exists because Phase 1 showed that normal per-PR review is not enough. A phase can look locally complete while still missing requirements from the foundation spec, implementation spec, acceptance criteria, fixture strategy, or development workflow docs.

Tasks:

1. Sync `main` after WO8 is merged.
2. Run the final local verification commands:
   - `pytest`
   - `ruff check .` if configured
   - `aam --help` or equivalent CLI help command
3. Run a comprehensive Codex review against the development docs.
4. Save the Codex review report to `docs/review/phase1_5_codex_final_review.md`.
5. Run a comprehensive Claude Code review against the development docs.
6. Save the Claude Code review report to `docs/review/phase1_5_claude_final_review.md`.
7. Create `docs/phase1_5_closeout_checklist.md`.
8. Fix all P0/P1 findings from either review.
9. If fixes are made, re-run tests and re-run both final reviews.
10. Do not mark Phase 1.5 complete until both final reports explicitly say there are no unresolved P0/P1 findings.
11. If P2/P3 findings remain, record them as Phase 2 follow-up risks or issues.
12. Only after both reviews pass, create or confirm the phase tag.

Development docs to review against include all repository dev docs that exist, and at minimum:

```text
Product Brief
Foundation & Roadmap Spec
Phase 1 implementation spec
Phase 1.5 implementation spec
Phase 1 handoff review
ADR 0001-0006
Phase 1.5 registry schema draft
Phase 1.5 profile / assembly / lock complexity note
Phase 1.5 technical spike note
CI / PR / issue templates
```

The final reviews must check at least:

```text
- Phase 1.5 scope compliance
- No production Phase 2+ functionality was introduced
- All work order deliverables exist
- All ADRs contain explicit decisions and consequences
- Storage / API / MCP / frontend / graph choices are not ambiguous
- UsageEvent / AuditLog / RejectionEvent placeholders are append-only and minimal
- Profile / Assembly / Lockfile boundaries are clear enough for Phase 3
- CI, issue template, PR template, and release convention are usable
- Tests and CLI smoke command pass
- Spike code, if any, is isolated under spikes/phase1_5/
- Phase 2 can start without reopening Phase 1.5 decisions
```

Deliverables:

```text
docs/review/phase1_5_codex_final_review.md
docs/review/phase1_5_claude_final_review.md
docs/phase1_5_closeout_checklist.md
```

Acceptance Criteria:

1. Codex final review exists and has no unresolved P0/P1 findings.
2. Claude Code final review exists and has no unresolved P0/P1 findings.
3. Both reviews explicitly reference the development docs as their review basis.
4. Any P0/P1 finding from either review is fixed and re-reviewed.
5. Any remaining P2/P3 finding is recorded as a follow-up issue or Phase 2 risk.
6. Final tests pass on `main`.
7. No Phase 1.5 milestone issue remains open.
8. No unexpected Phase 1.5 PR remains open.
9. The phase tag is created only after both final reviews pass.

## 10. GitHub Milestone and Issues

Create one milestone:

```text
Phase 1.5 — Technical Spike Checkpoint
```

Create one issue per work order:

```text
WO1 — Phase 1 Handoff Audit
WO2 — Registry Storage Spike and ADR
WO3 — Usage / Audit / Rejection Event Placeholder ADR
WO4 — API and MCP Framework Spike
WO5 — Profile / Assembly / Lockfile Complexity Note
WO6 — Frontend and Graph Stack ADR
WO7 — CI, GitHub Templates, and Release Convention
WO8 — Final Phase 1.5 Technical Spike Note
WO9 — Final Dual AI Review and Phase Closeout
```

Suggested labels:

```text
phase-1.5
work-order
docs
adr
spike
ci
```

Use `spike` for WO2/WO4/WO6 if actual probe code is added.
Use `docs` for all work orders.
Use `ci` for WO7.
Use `review` for WO9 if that label exists or can be created.

## 11. Acceptance Criteria

Phase 1.5 is complete when:

1. The Phase 1.5 milestone exists.
2. All WO1-WO9 issues exist and are closed.
3. All Phase 1.5 PRs are squash-merged.
4. `docs/phase1_handoff_review.md` exists.
5. ADRs 0001-0006 exist.
6. `docs/phase1_5_registry_schema_draft.md` exists.
7. `docs/phase1_5_profile_assembly_lock_complexity_note.md` exists.
8. `docs/phase1_5_technical_spike_note.md` exists.
9. `docs/review/phase1_5_codex_final_review.md` exists and has no unresolved P0/P1 findings.
10. `docs/review/phase1_5_claude_final_review.md` exists and has no unresolved P0/P1 findings.
11. `docs/phase1_5_closeout_checklist.md` exists.
12. CI passes on main.
13. Local tests pass on main.
14. No production Phase 2+ capabilities were introduced.
15. Phase 2 implementation spec can be written without making storage/API/MCP/frontend/graph/CI choices from scratch.
16. The phase tag is created only after both final AI reviews pass.

## 12. Testing Plan

Because Phase 1.5 is a technical spike and documentation phase, testing focuses on preventing regressions and validating probes.

Run per work order:

```bash
pytest
ruff check .  # if configured
aam --help
```

For work orders with probes, run the probe-specific smoke command documented in the probe README.

For WO7, confirm GitHub Actions passes on the PR.

For final verification, run:

```bash
git checkout main
git pull --ff-only
pytest
ruff check .  # if configured
aam --help
```

Then verify:

```bash
gh issue list --milestone "Phase 1.5 — Technical Spike Checkpoint" --state open
gh pr list --state open
```

Both should show no unexpected remaining Phase 1.5 work.

For WO9 final dual review, additionally verify:

```bash
test -f docs/review/phase1_5_codex_final_review.md
test -f docs/review/phase1_5_claude_final_review.md
test -f docs/phase1_5_closeout_checklist.md
```

The phase is not complete unless both final review reports explicitly state that no unresolved P0/P1 findings remain.

## 13. Risks and Mitigations

### Risk 1 — Spike Becomes Production Implementation

Problem:

Codex or Claude Code may implement Phase 2/3/4 features while trying to validate decisions.

Mitigation:

All probe code must stay under `spikes/phase1_5/`. Production directories should not receive API, MCP, store, frontend, or graph UI implementations.

### Risk 2 — Too Many ADRs Without Actionable Decisions

Problem:

Phase 1.5 could produce vague documents that do not help Phase 2.

Mitigation:

Each ADR must include:

```text
Decision
Status
Context
Options Considered
Chosen Option
Consequences
Out-of-scope
Follow-up Work
```

### Risk 3 — Storage Choice Reopens in Phase 2

Problem:

If the storage ADR is not specific enough, Phase 2 will repeat the debate.

Mitigation:

ADR 0001 must explicitly choose SQLite as primary unless the spike finds a concrete blocker.

### Risk 4 — MCP Server Starts Too Early

Problem:

MCP implementation may duplicate future API/assembly logic.

Mitigation:

WO4 probe must only validate framework fit. It must not implement production tools.

### Risk 5 — Frontend Stack Overcomplication

Problem:

Choosing Next.js or heavy dashboard infrastructure too early can overcomplicate Phase 6.

Mitigation:

Select React + Vite + TypeScript for a local asset browser unless a hard requirement contradicts it.

### Risk 6 — Graph Library Selected for Workflow Editing Instead of Relationship Graph

Problem:

React Flow may be attractive but is optimized for node-based UI/editors rather than graph relation analysis.

Mitigation:

Select Cytoscape.js as primary graph library. Keep React Flow as optional future flow renderer only.

### Risk 7 — Phase Closeout Relies Only on Per-PR Review

Problem:

Per-work-order reviews may miss cross-document inconsistencies or missing acceptance criteria.

Mitigation:

WO9 requires both Codex and Claude Code to perform full-phase reviews against the development docs. Phase 1.5 cannot close until both reviews have no unresolved P0/P1 findings.

### Risk 8 — Event Model Becomes Governance System Too Early

Problem:

Usage/rejection placeholders may become a premature governance workflow.

Mitigation:

Keep them append-only and minimal. Full governance remains later.

## 14. Review Checklist

For each Phase 1.5 PR, verify:

- [ ] It implements only the current work order.
- [ ] It does not introduce production Phase 2+ functionality.
- [ ] Any spike code is isolated under `spikes/phase1_5/`.
- [ ] ADRs have clear decisions and consequences.
- [ ] Tests pass locally.
- [ ] CI passes.
- [ ] `ruff check .` passes if configured.
- [ ] `aam --help` still works.
- [ ] Claude Code CLI review has no unresolved P0/P1 findings.
- [ ] PR scope is limited and reviewable.
- [ ] For WO9, Codex final review has no unresolved P0/P1 findings.
- [ ] For WO9, Claude Code final review has no unresolved P0/P1 findings.

## 15. Phase 1.5 Completion Definition

Phase 1.5 can be considered complete only when all work orders are merged, the final technical spike note confirms the decisions below, and both final AI review reports have no unresolved P0/P1 findings:

```text
registry storage: SQLite
registry export: deterministic JSON
future analytics: DuckDB optional
event placeholders: UsageEvent / AuditLog / RejectionEvent
API framework: FastAPI
MCP framework: official MCP Python SDK
frontend: React + Vite + TypeScript
graph visualization: Cytoscape.js
composition boundary: ProfileClosure / Discovery / AssemblyPlan / PackageLock separated
CI/release: stable GitHub PR workflow with phase tags
final review: Codex and Claude Code dual review passed
```

Recommended tag after completion:

```text
phase-1.5-technical-spike-checkpoint
```

If using semver, Phase 1.5 does not necessarily require a new semver release because it is mostly documentation and spike work. If the repository uses semver tags for every phase checkpoint, use:

```text
v0.1.5
```

Otherwise keep semver for functional milestones and use the phase tag only.

## 16. Handoff to Phase 2

Phase 2 should start from these Phase 1.5 outputs:

```text
docs/phase1_handoff_review.md
docs/adr/0001-registry-storage.md
docs/phase1_5_registry_schema_draft.md
docs/adr/0002-usage-audit-rejection-events.md
docs/phase1_5_technical_spike_note.md
docs/review/phase1_5_codex_final_review.md
docs/review/phase1_5_claude_final_review.md
docs/phase1_5_closeout_checklist.md
```

Phase 2 should then implement:

```text
Persistent Registry
RegistryStore
Registry rebuild
RegistryService backed by SQLite
AssetQueryService
GraphQueryService
StatsService
SourceAdapter interface
LocalDirectorySourceAdapter
local adopt import
local copy/snapshot import
GitHubSourceAdapter v0
ImportRun report
UsageEvent / AuditLog placeholder store
CLI usability improvements
JSON output mode
```

Phase 2 should not reopen the basic storage/API/MCP/frontend/graph decisions unless Phase 1.5 explicitly recorded a blocker.
