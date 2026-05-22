# ADR 0004: Composition, Assembly, and Lock Boundary

## Status

Accepted (Phase 1.5), 2026-05-22.

## Decision

Phase 3 should implement composition, assembly, lockfile, and materialization-preview behavior through separate services:

- `ProfileClosureService`
- `DiscoveryService`
- `AssemblyPlanner`
- `AssemblyPlanValidator`
- approval boundary
- `LockBuilder`
- `MaterializationPreviewService`

These boundaries must remain separate. Phase 3 should not collapse profile closure, discovery, planning, validation, lock building, and preview rendering into one large service.

Phase 3 should implement minimal reason-code explain/validate inside the composition pipeline so CLI users and tests can understand selected, excluded, warned, and missing assets. The fuller agent-facing explain/validate HTTP API belongs to Phase 4A Local Agent Gateway API.

Phase 1.5 does not implement any production profile closure, assembly planning, package lock generation, or materialization code.

All services should receive a registry query boundary from the application layer. Phase 3 should define this as a shared query protocol or service facade over the Phase 2 registry store, not as service-owned storage.

## Context

Foundation and Product docs define three related but distinct paths:

```text
Human Profile
  -> Profile closure
  -> Package Lock
  -> Materialization

Task + target host
  -> Discovery
  -> Assembly Plan
  -> Approval
  -> Package Lock
  -> Materialization

Task + base Profile
  -> Discovery with base profile
  -> Assembly Plan with profile_delta
  -> Approval
  -> Package Lock
  -> Materialization
```

Phase 3 is the first phase that turns the registry from "manage and query assets" into "compose and resolve assets." It carries real complexity: dependency closure, trust and permission warnings, target compatibility, profile deltas, reason codes, policy snapshots, lockfile reproducibility, and preview rendering.

If these responsibilities are implemented as one service, later API/MCP/UI adapters will either duplicate logic or expose inconsistent decisions. Keeping the boundaries separate preserves testability and lets CLI, API, MCP, and Web UI call the same services later.

## Service Boundary Decisions

### ProfileClosureService

Owns deterministic expansion of a persisted profile into a closed asset set.

Inputs:

- profile id or qualified profile id;
- registry query service;
- optional target host override;
- policy context;
- closure options such as include archived or fail on warnings.

Outputs:

- profile closure result;
- selected assets;
- resolved dependency closure;
- warnings;
- reason codes;
- missing or invalid references;
- closure summary for CLI/API presentation.

Does not:

- discover task-specific assets;
- create an Assembly Plan;
- create a Package Lock;
- render or write files.

### DiscoveryService

Owns deterministic candidate discovery from registry metadata and Asset Cards.

Inputs:

- task text or structured discovery request;
- target host;
- optional base profile id;
- asset filters;
- trust/visibility/permission constraints;
- registry query service.

Outputs:

- candidate assets;
- excluded assets with reason codes;
- missing capability notes;
- discovery warnings;
- candidate scoring or ranking metadata if Phase 3 includes a minimal rule-based ranker.

Does not:

- compute final profile closure;
- approve assets;
- create lockfiles;
- read full content by default.

### AssemblyPlanner

Owns construction of a task-level Assembly Plan from discovery results and optional base profile closure.

Inputs:

- discovery request;
- discovery candidates;
- optional base profile closure;
- target host;
- policy context;
- context budget hints;
- planner options.

Outputs:

- Assembly Plan;
- selected assets;
- excluded assets;
- `profile_delta` when a base profile exists;
- warnings;
- reason codes;
- rationale entries;
- risk summaries;
- missing dependencies or capabilities;
- estimated context cost.

Does not:

- perform final lockfile hashing;
- write files;
- bypass validator or policy;
- make irreversible governance changes.

### Approval Boundary

Owns the transition from a valid Assembly Plan or Profile closure to an approved input for LockBuilder.

Phase 3 may implement this as a simple CLI confirmation or explicit policy-approved marker rather than a standalone service. The boundary still must be modeled so LockBuilder never treats "valid" as the same thing as "approved."

Inputs:

- Profile closure or Assembly Plan;
- validation report;
- warnings;
- policy context;
- user or policy approval decision.

Outputs:

- approval record or approval token;
- accepted warnings;
- rejected warnings or rejection reason codes;
- approval timestamp and actor metadata when available.

Does not:

- mutate the Assembly Plan;
- choose additional assets;
- build the lockfile;
- materialize assets.

### AssemblyPlanValidator

Owns validation of an Assembly Plan before lock generation.

Inputs:

- Assembly Plan;
- registry query service;
- policy context;
- target host constraints;
- validation options.

Outputs:

- validation report;
- blocking errors;
- warnings;
- reason codes;
- dependency closure validation;
- policy compatibility summary.

Does not:

- mutate the plan;
- approve the plan;
- build the lockfile;
- materialize assets.

### LockBuilder

Owns conversion of an approved Profile closure or approved Assembly Plan into a reproducible Package Lock.

Inputs:

- approved profile closure or approved Assembly Plan;
- registry query service;
- policy snapshot;
- target host;
- materialization assumptions;
- lock metadata.

Outputs:

- Package Lock;
- exact assets and versions;
- content hashes;
- source provenance;
- dependency graph;
- trust and permission snapshot;
- accepted warnings;
- policy snapshot reference or embedded snapshot.
- materialization assumptions;
- source task and base profile metadata when applicable.

Does not:

- choose assets;
- resolve task intent;
- render host files;
- rewrite manifest state.

### MaterializationPreviewService

Owns dry-run rendering of a Package Lock into target host output plans.

Inputs:

- Package Lock;
- target host or renderer;
- workspace paths;
- preview options;
- previous preview/materialization snapshot for diff.

Outputs:

- preview artifact;
- markdown preview artifact;
- JSON preview artifact;
- target file plan;
- warnings;
- diff summary;
- unsupported target notes;
- reproducibility metadata.

Does not:

- write target files in Phase 3 unless explicitly scoped later;
- approve materialization;
- build lockfiles;
- select assets.

## Phase 3 Explain/Validate Boundary

Phase 3 should implement minimal explain/validate as service output, not as a full network API.

Minimal Phase 3 explain/validate should include:

- reason codes for selected assets;
- reason codes for excluded assets;
- dependency closure status;
- warnings for trust, lifecycle, permissions, target compatibility, and context cost;
- missing assets or missing capabilities;
- `profile_delta` explanation when a base profile is used;
- validation report suitable for CLI and snapshot tests.

Phase 4A should implement the richer Local Agent Gateway explain/validate API:

- stable HTTP request/response schemas;
- detailed machine-readable response shapes;
- request correlation and event placeholder integration;
- degraded-mode error responses;
- full agent-facing documentation;
- policy/approval interaction shapes.

This split lets Phase 3 remain testable and CLI-first while avoiding premature API contract design before the core algorithms exist.

## Rationale

The services answer different product questions:

| Service | Question |
| --- | --- |
| `ProfileClosureService` | What does this saved profile include after dependencies are resolved? |
| `DiscoveryService` | What assets might help this task and target? |
| `AssemblyPlanner` | What should this agent use for this task right now? |
| `AssemblyPlanValidator` | Is this plan internally valid and policy-compatible? |
| Approval boundary | Has a human or policy accepted this valid closure/plan and its warnings? |
| `LockBuilder` | What exact approved assets, hashes, provenance, and policy snapshot were resolved? |
| `MaterializationPreviewService` | What would be written for this target host? |

Separating these services keeps Phase 3 from becoming a monolith and protects Phase 4 API/MCP adapters from embedding business logic.

## Consequences

Phase 3 implementation specs should:

- define small typed models for each boundary;
- write tests per service before adding integrated CLI flows;
- keep reason codes stable and deterministic;
- use snapshot tests for Assembly Plan, Package Lock, and preview outputs;
- reject or warn on policy issues through validator outputs, not hidden side effects;
- require explicit approval input before lock generation;
- keep CLI commands as adapters over services.

Phase 3 implementation specs should avoid:

- adding HTTP API routes;
- adding MCP tools;
- adding Web UI;
- writing materialized files before preview/approval semantics are stable;
- generating Package Lock directly from DiscoveryService without AssemblyPlanValidator;
- letting LockBuilder choose assets.

## Non-goals

- No production profile closure code in Phase 1.5.
- No production discovery service code in Phase 1.5.
- No production assembly planner code in Phase 1.5.
- No production assembly validator code in Phase 1.5.
- No production package lock generation in Phase 1.5.
- No production materialization preview service in Phase 1.5.
- No HTTP API, MCP server, Web UI, graph UI, or dashboard.
