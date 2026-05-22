# Profile, Assembly, and Lockfile Complexity Note

## Purpose

This note defines the Phase 3 complexity boundary for Profile closure, Discovery, Assembly Plan, Package Lock, and Materialization Preview.

It is not an implementation spec and does not introduce production code. It provides enough structure for a Phase 3 implementation spec to start without reopening Phase 1.5 decisions.

## Concept Boundaries

| Concept | Nature | Lifecycle | Main question |
| --- | --- | --- | --- |
| Package | Source asset container described by manifest. | Long-lived source object. | What assets and profiles does this package declare? |
| Profile | Human-governed scenario baseline. | Long-lived user object. | What do I usually use for this scenario? |
| Assembly Plan | Task-level composition proposal. | One task or short-lived proposal. | What should this agent use for this task right now? |
| Package Lock | Approved reproducibility snapshot. | Durable audit/replay object. | What exact assets, versions, hashes, provenance, policies, and dependencies were approved? |
| Materialization Preview | Dry-run target output plan. | Per lock/target attempt. | What files/configs would be produced for this target host? |
| Materialized Bundle | Actual rendered target output. | Host-consumed artifact. | What was actually written or packaged? |

Phase 3 should implement the minimum useful path:

```text
Profile -> ProfileClosureService -> Approval boundary -> Package Lock -> MaterializationPreviewService

Task + target_host -> DiscoveryService -> AssemblyPlanner -> AssemblyPlanValidator -> Approval boundary -> Package Lock -> MaterializationPreviewService

Task + base Profile -> ProfileClosureService -> DiscoveryService -> AssemblyPlanner with profile_delta -> AssemblyPlanValidator -> Approval boundary -> Package Lock -> MaterializationPreviewService
```

## Service Contracts

The contracts below are pseudo-contracts. They should become typed Python models and service classes during Phase 3.

The registry query service is supplied by the application layer to each service. Phase 3 should define a shared registry query protocol or facade over the Phase 2 registry store so services do not own storage or create separate query lifecycles.

### ProfileClosureService

Responsibility: resolve a saved profile into a closed asset set.

Inputs:

- `profile_id` or `profile_qualified_id`;
- `RegistryService` or future registry query service;
- `target_host`;
- `policy_context`;
- `closure_options`;
- optional context budget.

Outputs:

- `ProfileClosureResult`;
- base profile metadata;
- selected asset ids;
- dependency closure asset ids;
- warnings;
- reason codes;
- missing or invalid references;
- estimated context cost;
- validation summary.

Important rules:

- The profile includes list is the baseline.
- Dependency closure must be deterministic.
- Missing references are validation errors, not silent skips.
- Blocked assets must fail closed unless an explicit future policy allows otherwise.
- Unreviewed or sandbox-only assets must produce warnings.

### DiscoveryService

Responsibility: produce task/target candidate assets from registry metadata and Asset Cards.

Inputs:

- `DiscoveryRequest`;
- task text or structured task metadata;
- `target_host`;
- optional `base_profile_id`;
- filters for type, tag, trust, lifecycle, host, permissions, and context budget;
- registry query service;
- policy context.

Outputs:

- `DiscoveryResult`;
- candidate asset cards;
- excluded assets and reason codes;
- missing capability notes;
- warnings;
- minimal score or rank metadata if Phase 3 includes rule-based ranking.

Important rules:

- Discovery should prefer Asset Card data over full content.
- Discovery must not bypass visibility, trust, lifecycle, permission, or target-host constraints.
- Phase 3 discovery should be rule-based and deterministic. Semantic search is out of scope.

### AssemblyPlanner

Responsibility: construct an Assembly Plan from discovery results and optional profile closure.

Inputs:

- `DiscoveryRequest`;
- `DiscoveryResult`;
- optional `ProfileClosureResult`;
- target host;
- policy context;
- context budget;
- planner options.

Outputs:

- `AssemblyPlan`;
- selected assets;
- excluded assets;
- missing assets/capabilities;
- warnings;
- reason codes;
- rationale entries;
- risk summaries;
- `profile_delta`;
- estimated context cost.

Important rules:

- With no base profile, the plan is built from task/target candidates.
- With a base profile, the plan treats the profile closure as baseline and records only task-specific add/remove/override/warn changes in `profile_delta`.
- The planner proposes; it does not lock or materialize.

### AssemblyPlanValidator

Responsibility: validate an Assembly Plan before lock generation.

Inputs:

- `AssemblyPlan`;
- registry query service;
- policy context;
- target host;
- validation options.

Outputs:

- validation report;
- blocking errors;
- warnings;
- reason codes;
- dependency closure check;
- policy compatibility check;
- host compatibility check.

Important rules:

- Validation should be deterministic.
- Errors block lock generation.
- Warnings may require explicit approval before LockBuilder runs.
- Validator must not mutate the Assembly Plan in place.

### Approval Boundary

Responsibility: convert a valid Profile closure or Assembly Plan into an approved input for LockBuilder.

Phase 3 can implement approval as a simple CLI confirmation, a policy-approved marker, or a small approval record. It does not need a standalone production approval service, but the boundary must be explicit so valid does not silently mean approved.

Inputs:

- `ProfileClosureResult` or `AssemblyPlan`;
- validation report;
- warnings;
- policy context;
- user or policy decision.

Outputs:

- approval record or approval token;
- accepted warning records;
- rejected warning records or rejection reason codes;
- actor metadata when available;
- approval timestamp.

Important rules:

- Approval does not mutate the saved Profile.
- Approval does not choose assets.
- LockBuilder must require explicit approval input.

### LockBuilder

Responsibility: build a reproducible Package Lock from an approved profile closure or approved Assembly Plan.

Inputs:

- approved `ProfileClosureResult` or approved `AssemblyPlan`;
- registry query service;
- policy snapshot;
- target host;
- accepted warnings;
- materialization assumptions;
- lock metadata.

Outputs:

- `PackageLock`;
- exact package ids and versions;
- exact asset ids and versions;
- content hashes;
- source provenance;
- dependency graph;
- trust and permission snapshot;
- policy snapshot;
- accepted warning records;
- materialization assumptions;
- created-for-task metadata when applicable;
- base profile metadata when applicable;
- reproducibility metadata.

Important rules:

- LockBuilder records final resolved facts. It does not select assets.
- Content hash is required for every locked file-backed asset.
- Policy snapshot is required for auditability.
- Package Lock is distinct from package manifest.

### MaterializationPreviewService

Responsibility: dry-run render a Package Lock into a target-host output plan.

Inputs:

- `PackageLock`;
- target host;
- renderer options;
- workspace/output paths;
- previous preview or materialization snapshot for diff;
- preview options.

Outputs:

- `MaterializationPreview`;
- generic markdown preview artifact;
- generic JSON preview artifact;
- target file plan;
- rendered content summaries or hashes;
- warnings;
- unsupported target notes;
- diff summary;
- reproducibility metadata.

Important rules:

- Preview must not write target files unless a later phase explicitly scopes materialization execution.
- Preview should be deterministic and snapshot-testable.
- Actual materialization and target-specific adapters are beyond Phase 1.5 and should be carefully scoped in later phases.
- Materialized Bundle remains the later output of actual materialization; Phase 3 preview describes what would become that bundle without writing it.

## Hard Problems

### Dependency Closure

Dependency closure must answer:

- which direct and transitive assets are required;
- whether every reference resolves;
- whether cycles exist;
- whether dependency trust/permissions/lifecycle state creates warnings or blockers;
- whether dependencies are compatible with target host.

Complexity risks:

- duplicate assets from profile baseline and dynamic discovery;
- transitive dependencies with broader permissions than the selected top-level asset;
- archived or blocked assets appearing only as dependencies;
- cycles or stale references introduced by imported packages in later phases.

Phase 3 should start with deterministic closure over existing registry dependencies and avoid cross-workspace dependency design.

### `profile_delta`

`profile_delta` explains how a task-level Assembly Plan differs from a base profile.

Minimum shape:

- `added`: assets added for this task;
- `removed`: base profile assets excluded for this task;
- `overridden`: baseline assets replaced by better task/host/policy matches;
- `warned`: retained baseline assets with warnings.

Complexity risks:

- distinguishing "removed because irrelevant" from "removed because blocked";
- representing dependency changes caused by one override;
- keeping the delta readable when many transitive dependencies change;
- avoiding destructive edits to the saved Profile.

Phase 3 should treat `profile_delta` as explanatory output on the Assembly Plan, not as a mutation of the Profile.

### Warnings

Warnings are non-blocking issues that must be visible before approval or lock generation.

Minimum warning categories:

- `trust_warning`;
- `permission_warning`;
- `lifecycle_warning`;
- `target_host_warning`;
- `context_cost_warning`;
- `dependency_warning`;
- `missing_capability_warning`.

Complexity risks:

- warning fatigue;
- inconsistent severity across CLI/API/MCP;
- hidden warnings becoming accepted in the Package Lock without user awareness.

Phase 3 should use stable warning codes and snapshot tests.

### Reason Codes

Reason codes explain decisions without requiring LLM-generated prose.

Minimum reason-code families:

- selected because task matched tags/type/target host;
- selected because profile baseline included it;
- selected because dependency closure required it;
- excluded because trust status blocked it;
- excluded because lifecycle status archived it;
- excluded because permissions exceeded policy;
- excluded because target host incompatible;
- warning because unreviewed/sandbox-only/high-risk;
- missing because required capability was unavailable.

Complexity risks:

- overfitting reason codes before the planner is stable;
- mixing human-facing prose with machine-readable codes;
- inconsistent codes across discovery, planner, validator, and lock builder.

Phase 3 should define a small stable set. Phase 4A can expose richer explain/validate response objects.

### Policy Snapshot

Package Lock needs a policy snapshot so a later user can understand what rules allowed the lock.

Minimum snapshot contents:

- target host;
- allowed trust statuses;
- denied trust statuses;
- permission allowances;
- accepted warnings;
- materialization assumptions;
- policy version or policy source reference.

Complexity risks:

- confusing current policy with lock-time policy;
- storing too much mutable policy data;
- making lock generation depend on network or remote policy state.

Phase 3 should store enough policy facts for reproducibility and auditability, not a full governance system.

## Phase 3 Minimal Explain/Validate

Phase 3 should implement minimal explain/validate as deterministic service output:

- CLI-readable explanation of selected/excluded/warned assets;
- machine-readable reason codes;
- validation report for Assembly Plan;
- dependency closure summary;
- `profile_delta` summary;
- Package Lock validation before preview.

Phase 3 should not implement a full explain/validate HTTP API. It should produce typed outputs that Phase 4A can expose later.

## Phase 4A Full Explain/Validate API

Phase 4A should wrap stable Phase 3 services in Local Agent Gateway endpoints:

- structured request/response schemas;
- request ids and event placeholder correlation;
- degraded-mode responses;
- detailed explain/validate objects;
- policy/approval response shapes;
- safe external-agent consumption.

This keeps Phase 3 focused on correctness and reproducibility while letting Phase 4A design the agent-facing contract once the service outputs are stable.

## Phase 3 Implementation Spec Skeleton

A future Phase 3 implementation spec should include:

1. typed models for closure, discovery, assembly plan, profile delta, validation result, package lock, and preview;
2. reason-code and warning-code vocabulary;
3. service boundaries and dependency graph;
4. deterministic fixture packages;
5. unit tests per service;
6. snapshot tests for plan, lock, and preview outputs;
7. CLI adapter commands over services;
8. explicit non-goals for API, MCP, Web UI, and actual materialization.

## Non-goals

- No production profile closure implementation in Phase 1.5.
- No production discovery implementation in Phase 1.5.
- No production assembly planner implementation in Phase 1.5.
- No production package lock implementation in Phase 1.5.
- No production materialization preview implementation in Phase 1.5.
- No actual materialization.
- No semantic search.
- No API, MCP server, Web UI, graph UI, dashboard, or team workspace.
